/**
 * Knowledge Graph Force-Directed Visualization
 * Uses D3.js v7 for rendering.
 * Edges that share a target or (source,target) pair are drawn as curved paths to avoid overlap.
 */

// State
let simulation = null;
let svg = null;
let g = null;  // Main group for zoom/pan
let zoom = null;  // Zoom behavior reference
let currentData = { nodes: [], edges: [] };

// DOM Elements
const entitySearchInput = document.getElementById('entity-search');
const searchResultsContainer = document.getElementById('search-results');
const centerIdInput = document.getElementById('center-id');
const hopsInput = document.getElementById('hops');
const hopsValue = document.getElementById('hops-value');
const maxNodesInput = document.getElementById('max-nodes');
const maxNodesValue = document.getElementById('max-nodes-value');
const includeAllCheckbox = document.getElementById('include-all');
const loadButton = document.getElementById('load-graph');
const resetButton = document.getElementById('reset-view');
const tooltip = document.getElementById('tooltip');
const detailPanel = document.getElementById('detail-panel');
const panelTitle = document.getElementById('panel-title');
const panelContent = document.getElementById('panel-content');
const closePanel = document.getElementById('close-panel');

// Search state
let searchTimeout = null;
let selectedSearchIndex = -1;

// Stats elements
const nodeCountEl = document.getElementById('node-count');
const edgeCountEl = document.getElementById('edge-count');
const totalEntitiesEl = document.getElementById('total-entities');
const totalRelationshipsEl = document.getElementById('total-relationships');
const truncatedWarning = document.getElementById('truncated-warning');

/** Single source of truth for entity type colors. Used for node fill and legend. */
const ENTITY_TYPE_COLORS = {
    disease: { color: '#e94560', label: 'Disease' },
    drug: { color: '#4fc3f7', label: 'Drug' },
    gene: { color: '#66bb6a', label: 'Gene' },
    protein: { color: '#ab47bc', label: 'Protein' },
    procedure: { color: '#ffa726', label: 'Procedure' },
    symptom: { color: '#ef5350', label: 'Symptom' },
    anatomy: { color: '#8d6e63', label: 'Anatomy' },
    biomarker: { color: '#26a69a', label: 'Biomarker' },
    pathway: { color: '#7e57c2', label: 'Pathway' },
    biologicalprocess: { color: '#5c6bc0', label: 'Biological process' },
    default: { color: '#78909c', label: 'Other' },
};

// Initialize
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupSVG();
    setupEventListeners();
    initLegend();

    // Check URL params for initial load
    const params = new URLSearchParams(window.location.search);
    const centerId = params.get('center_id');
    if (centerId) {
        centerIdInput.value = centerId;
        loadGraph();
    } else {
        // On first visit with no params, show entire graph (inputs stay enabled so user can search/enter ID)
        includeAllCheckbox.checked = true;
        loadGraph();
    }
}

function setupSVG() {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    svg = d3.select('#graph-svg')
        .attr('viewBox', [0, 0, width, height]);
    
    // Add arrow marker definition
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '-0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('orient', 'auto')
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .append('path')
        .attr('d', 'M 0,-5 L 10,0 L 0,5')
        .attr('fill', '#999');
    
    // Create main group for zoom/pan
    g = svg.append('g');
    
    // Setup zoom behavior
    zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Handle window resize
    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;
        svg.attr('viewBox', [0, 0, newWidth, newHeight]);
        if (simulation) {
            simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }
    });
}

function setupEventListeners() {
    // Search input with debounce
    entitySearchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Clear previous timeout
        if (searchTimeout) clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            hideSearchResults();
            return;
        }
        
        // Debounce: wait 300ms after typing stops
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Keyboard navigation for search results
    entitySearchInput.addEventListener('keydown', (e) => {
        const items = searchResultsContainer.querySelectorAll('.search-result-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedSearchIndex = Math.min(selectedSearchIndex + 1, items.length - 1);
            updateSearchSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedSearchIndex = Math.max(selectedSearchIndex - 1, 0);
            updateSearchSelection(items);
        } else if (e.key === 'Enter' && selectedSearchIndex >= 0) {
            e.preventDefault();
            items[selectedSearchIndex]?.click();
        } else if (e.key === 'Escape') {
            hideSearchResults();
        }
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!entitySearchInput.contains(e.target) && !searchResultsContainer.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    // Update display values for range inputs
    hopsInput.addEventListener('input', () => {
        hopsValue.textContent = hopsInput.value;
    });
    
    maxNodesInput.addEventListener('input', () => {
        maxNodesValue.textContent = maxNodesInput.value;
    });
    
    // Toggle center_id input based on include_all checkbox
    includeAllCheckbox.addEventListener('change', () => {
        centerIdInput.disabled = includeAllCheckbox.checked;
        entitySearchInput.disabled = includeAllCheckbox.checked;
    });
    
    // Load graph button
    loadButton.addEventListener('click', loadGraph);
    
    // Enter key in center_id input
    centerIdInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadGraph();
    });
    
    // Reset view button
    resetButton.addEventListener('click', resetView);
    
    // Close detail panel
    closePanel.addEventListener('click', () => {
        detailPanel.classList.add('hidden');
    });
}

// Search functionality
async function performSearch(query) {
    showSearchLoading();
    
    try {
        const response = await fetch(`/api/v1/graph/search?q=${encodeURIComponent(query)}&limit=20`);
        if (!response.ok) {
            throw new Error('Search failed');
        }
        
        const data = await response.json();
        renderSearchResults(data.results, data.total);
        
    } catch (error) {
        console.error('Search error:', error);
        searchResultsContainer.innerHTML = '<div class="search-no-results">Search failed</div>';
        searchResultsContainer.classList.remove('hidden');
    }
}

function renderSearchResults(results, total) {
    selectedSearchIndex = -1;
    
    if (results.length === 0) {
        searchResultsContainer.innerHTML = '<div class="search-no-results">No entities found</div>';
        searchResultsContainer.classList.remove('hidden');
        return;
    }
    
    let html = results.map((result, index) => `
        <div class="search-result-item" data-entity-id="${escapeHtml(result.entity_id)}" data-index="${index}">
            <div class="search-result-name">${escapeHtml(result.name)}</div>
            <div class="search-result-type">${escapeHtml(result.entity_type)}</div>
            <div class="search-result-id">${escapeHtml(result.entity_id)}</div>
        </div>
    `).join('');
    
    if (total > results.length) {
        html += `<div class="search-no-results">${total - results.length} more results...</div>`;
    }
    
    searchResultsContainer.innerHTML = html;
    searchResultsContainer.classList.remove('hidden');
    
    // Add click handlers
    searchResultsContainer.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const entityId = item.dataset.entityId;
            selectSearchResult(entityId);
        });
    });
}

function selectSearchResult(entityId) {
    centerIdInput.value = entityId;
    entitySearchInput.value = '';
    hideSearchResults();
    includeAllCheckbox.checked = false;
    centerIdInput.disabled = false;
    entitySearchInput.disabled = false;
    loadGraph();
}

function updateSearchSelection(items) {
    items.forEach((item, i) => {
        item.classList.toggle('selected', i === selectedSearchIndex);
    });
    
    // Scroll selected item into view
    if (selectedSearchIndex >= 0 && items[selectedSearchIndex]) {
        items[selectedSearchIndex].scrollIntoView({ block: 'nearest' });
    }
}

function showSearchLoading() {
    searchResultsContainer.innerHTML = '<div class="search-loading">Searching...</div>';
    searchResultsContainer.classList.remove('hidden');
}

function hideSearchResults() {
    searchResultsContainer.classList.add('hidden');
    selectedSearchIndex = -1;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadGraph() {
    const includeAll = includeAllCheckbox.checked;
    const centerId = centerIdInput.value.trim();
    const hops = parseInt(hopsInput.value);
    const maxNodes = parseInt(maxNodesInput.value);
    
    if (!includeAll && !centerId) {
        showError('Please enter a center entity ID or check "Show entire graph"');
        return;
    }
    
    // Build URL
    let url = `/api/v1/graph/subgraph?hops=${hops}&max_nodes=${maxNodes}`;
    if (includeAll) {
        url += '&include_all=true';
    } else {
        url += `&center_id=${encodeURIComponent(centerId)}`;
    }
    
    // Show loading state
    showLoading();
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load graph');
        }
        
        const data = await response.json();
        currentData = data;
        
        // Update stats
        updateStats(data);
        
        // Render graph
        renderGraph(data);
        
    } catch (error) {
        showError(error.message);
    }
}

function updateStats(data) {
    nodeCountEl.textContent = data.nodes.length;
    edgeCountEl.textContent = data.edges.length;
    totalEntitiesEl.textContent = data.total_entities;
    totalRelationshipsEl.textContent = data.total_relationships;
    
    if (data.truncated) {
        truncatedWarning.classList.remove('hidden');
    } else {
        truncatedWarning.classList.add('hidden');
    }
}

function renderGraph(data) {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Clear existing content
    g.selectAll('*').remove();
    
    if (data.nodes.length === 0) {
        showError('No nodes found for the given criteria');
        return;
    }
    
    // Assign curve offset so edges converging on the same node (or same pair) bow out
    const byTarget = {};
    const byPair = {};
    data.edges.forEach(d => {
        const t = d.target;
        const p = `${d.source}\0${d.target}`;
        if (!byTarget[t]) byTarget[t] = [];
        if (!byPair[p]) byPair[p] = [];
        byTarget[t].push(d);
        byPair[p].push(d);
    });
    const links = data.edges.map(d => {
        const t = d.target;
        const p = `${d.source}\0${d.target}`;
        const targetGroup = byTarget[t];
        const pairGroup = byPair[p];
        const nTarget = targetGroup.length;
        const nPair = pairGroup.length;
        const idxTarget = targetGroup.indexOf(d);
        const idxPair = pairGroup.indexOf(d);
        // Offset when multiple edges share target or share (source,target)
        const spread = 28;
        let curveOffset = 0;
        if (nTarget > 1) curveOffset += (idxTarget - (nTarget - 1) / 2) * spread;
        if (nPair > 1) curveOffset += (idxPair - (nPair - 1) / 2) * spread * 0.5;
        return {
            ...d,
            source: d.source,
            target: d.target,
            curveOffset
        };
    });
    
    // Create nodes data
    const nodes = data.nodes.map(d => ({ ...d }));
    
    // Create simulation
    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links)
            .id(d => d.id)
            .distance(150))
        .force('charge', d3.forceManyBody()
            .strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(40));
    
    // Create link elements (path for curved edges)
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('path')
        .data(links)
        .join('path')
        .attr('class', 'link')
        .attr('stroke', '#999')
        .attr('stroke-width', 1.5)
        .attr('fill', 'none')
        .attr('marker-end', 'url(#arrowhead)')
        .on('click', (event, d) => showEdgeDetails(d))
        .on('mouseenter', (event, d) => showEdgeTooltip(event, d))
        .on('mouseleave', hideTooltip);
    
    // Create link labels
    const linkLabel = g.append('g')
        .attr('class', 'link-labels')
        .selectAll('text')
        .data(links)
        .join('text')
        .attr('class', 'link-label')
        .text(d => d.label);
    
    // Create node elements
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', (event, d) => showNodeDetails(d))
        .on('dblclick', (event, d) => recenterOn(d.id))
        .on('mouseenter', (event, d) => showNodeTooltip(event, d))
        .on('mouseleave', hideTooltip);
    
    // Add circles to nodes (fill from ENTITY_TYPE_COLORS)
    node.append('circle')
        .attr('r', d => d.id === data.center_id ? 12 : 8)
        .attr('fill', d => {
            const typeClass = getNodeTypeClass(d.entity_type);
            return (ENTITY_TYPE_COLORS[typeClass] || ENTITY_TYPE_COLORS.default).color;
        });
    
    // Add labels to nodes
    node.append('text')
        .attr('dy', 20)
        .text(d => truncateLabel(d.label, 15));
    
    // Quadratic path: source -> control -> target; control offset perpendicular to line
    function linkPath(d) {
        const sx = d.source.x;
        const sy = d.source.y;
        const tx = d.target.x;
        const ty = d.target.y;
        const offset = d.curveOffset || 0;
        if (offset === 0) {
            return `M${sx},${sy} L${tx},${ty}`;
        }
        const mx = (sx + tx) / 2;
        const my = (sy + ty) / 2;
        const dx = tx - sx;
        const dy = ty - sy;
        const len = Math.sqrt(dx * dx + dy * dy) || 1;
        const px = (-dy / len) * offset;
        const py = (dx / len) * offset;
        const cpx = mx + px;
        const cpy = my + py;
        return `M${sx},${sy} Q${cpx},${cpy} ${tx},${ty}`;
    }

    // Update positions on tick
    simulation.on('tick', () => {
        link.attr('d', linkPath);

        // Place labels at 1/4 of the curve offset so they sit closer to the edge
        const labelOffsetScale = 0.25;
        linkLabel
            .attr('x', d => {
                const sx = d.source.x, sy = d.source.y, tx = d.target.x, ty = d.target.y;
                const o = (d.curveOffset || 0) * labelOffsetScale;
                if (o === 0) return (sx + tx) / 2;
                const mx = (sx + tx) / 2, my = (sy + ty) / 2;
                const dx = tx - sx, dy = ty - sy, len = Math.sqrt(dx * dx + dy * dy) || 1;
                return mx + (-dy / len) * o;
            })
            .attr('y', d => {
                const sx = d.source.x, sy = d.source.y, tx = d.target.x, ty = d.target.y;
                const o = (d.curveOffset || 0) * labelOffsetScale;
                if (o === 0) return (sy + ty) / 2;
                const mx = (sx + tx) / 2, my = (sy + ty) / 2;
                const dx = tx - sx, dy = ty - sy, len = Math.sqrt(dx * dx + dy * dy) || 1;
                return my + (dx / len) * o;
            });

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

/** Map API entity_type (lowercase) to ENTITY_TYPE_COLORS key. Extend when adding new backend types. */
const TYPE_TO_LEGEND_KEY = {
    anatomicalstructure: 'anatomy',
    hormone: 'default',
    enzyme: 'default',
};

function getNodeTypeClass(entityType) {
    const type = (entityType || '').toLowerCase().replace(/\s+/g, '');
    return TYPE_TO_LEGEND_KEY[type] || (ENTITY_TYPE_COLORS.hasOwnProperty(type) ? type : 'default');
}

function initLegend() {
    const container = document.getElementById('graph-legend');
    if (!container) return;
    const types = Object.entries(ENTITY_TYPE_COLORS);
    container.innerHTML =
        '<div class="legend-title">Entity types</div>' +
        types
            .map(
                ([key, { color, label }]) =>
                    `<div class="legend-item"><span class="legend-dot" style="background-color:${color}"></span>${escapeHtml(label)}</div>`
            )
            .join('');
}

function truncateLabel(label, maxLength) {
    if (!label) return '';
    return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
}

// Drag handlers
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Tooltip (position: fixed so it follows cursor in viewport)
function showTooltip(event, text) {
    tooltip.textContent = text;
    tooltip.classList.remove('hidden');
    const offset = 12;
    tooltip.style.left = (event.clientX + offset) + 'px';
    tooltip.style.top = (event.clientY + offset) + 'px';
}

function showNodeTooltip(event, d) {
    let text = `${d.label}\n(${d.entity_type})`;
    const p = (d.properties || {});
    if (p.first_seen_document != null) text += `\nFirst seen: ${p.first_seen_document}`;
    if (p.total_mentions != null) text += `\nMentions: ${p.total_mentions}`;
    showTooltip(event, text);
}

function showEdgeTooltip(event, d) {
    let text = d.label;
    const p = (d.properties || {});
    if (p.evidence_count != null) text += `\nEvidence: ${p.evidence_count}`;
    if (p.strongest_evidence_quote) text += `\n"${truncateLabel(p.strongest_evidence_quote, 60)}"`;
    showTooltip(event, text);
}

function hideTooltip() {
    tooltip.classList.add('hidden');
}

// Detail panel
function showNodeDetails(node) {
    panelTitle.textContent = node.label || node.id;
    
    let html = '';
    const props = node.properties || {};
    
    html += createProperty('Entity ID', props.entity_id);
    html += createProperty('Type', props.entity_type);
    html += createProperty('Name', props.name);
    html += createProperty('Status', props.status);
    html += createProperty('Confidence', props.confidence);
    html += createProperty('Usage Count', props.usage_count);
    
    // Make source a clickable link if it's a PMC ID
    if (props.source) {
        const sourceLink = formatSourceLink(props.source);
        html += createProperty('Source', sourceLink);
    }
    
    if (props.canonical_url) {
        html += createProperty('Canonical URL', 
            `<a href="${props.canonical_url}" target="_blank">${props.canonical_url}</a>`);
    }
    
    if (props.synonyms && props.synonyms.length > 0) {
        html += createProperty('Synonyms', props.synonyms.join(', '));
    }

    // Provenance summary
    if (props.first_seen_document != null) {
        const docLink = formatSourceLink(props.first_seen_document);
        html += createProperty('First seen document', docLink);
    }
    if (props.first_seen_section != null) {
        html += createProperty('First seen section', props.first_seen_section);
    }
    if (props.total_mentions != null) {
        html += createProperty('Total mentions', props.total_mentions);
    }
    if (props.supporting_documents && props.supporting_documents.length > 0) {
        const linked = props.supporting_documents.map(d => formatSourceLink(d)).join(', ');
        html += createProperty('Supporting documents', linked);
    }

    panelContent.innerHTML = html;
    detailPanel.classList.remove('hidden');
}

/**
 * Format a source identifier as a clickable link when possible.
 * Supports PMC IDs (PubMed Central) and PMID (PubMed).
 */
function formatSourceLink(source) {
    if (!source) return '';
    
    // PMC ID format: PMC followed by digits (e.g., PMC10759991)
    const pmcMatch = source.match(/^PMC(\d+)$/i);
    if (pmcMatch) {
        const pmcUrl = `https://www.ncbi.nlm.nih.gov/pmc/articles/${source}/`;
        return `<a href="${pmcUrl}" target="_blank" title="View on PubMed Central">${source}</a>`;
    }
    
    // PMID format: just digits or "PMID:" prefix
    const pmidMatch = source.match(/^(?:PMID[:\s]*)?(\d{6,9})$/i);
    if (pmidMatch) {
        const pmid = pmidMatch[1];
        const pmidUrl = `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
        return `<a href="${pmidUrl}" target="_blank" title="View on PubMed">PMID:${pmid}</a>`;
    }
    
    // DOI format
    if (source.startsWith('10.') || source.toLowerCase().startsWith('doi:')) {
        const doi = source.replace(/^doi:/i, '');
        const doiUrl = `https://doi.org/${doi}`;
        return `<a href="${doiUrl}" target="_blank" title="View via DOI">${source}</a>`;
    }
    
    // Return as-is if no pattern matches
    return source;
}

function showEdgeDetails(edge) {
    panelTitle.textContent = edge.label;
    
    let html = '';
    const props = edge.properties || {};
    
    html += createProperty('Predicate', props.predicate);
    html += createProperty('Subject', props.subject_id);
    html += createProperty('Object', props.object_id);
    html += createProperty('Confidence', props.confidence);
    
    // Make source documents clickable links
    if (props.source_documents && props.source_documents.length > 0) {
        const linkedDocs = props.source_documents
            .map(doc => formatSourceLink(doc))
            .join(', ');
        html += createProperty('Source Documents', linkedDocs);
    }

    // Evidence summary
    if (props.evidence_count != null) {
        html += createProperty('Evidence count', props.evidence_count);
    }
    if (props.evidence_confidence_avg != null) {
        html += createProperty('Evidence confidence (avg)', props.evidence_confidence_avg);
    }
    if (props.strongest_evidence_quote) {
        html += createProperty('Strongest evidence', escapeHtml(props.strongest_evidence_quote));
    }

    panelContent.innerHTML = html;
    detailPanel.classList.remove('hidden');
}

function createProperty(label, value) {
    if (value === null || value === undefined || value === '') return '';
    return `
        <div class="property">
            <div class="property-label">${label}</div>
            <div class="property-value">${value}</div>
        </div>
    `;
}

// Recenter graph on a node
function recenterOn(entityId) {
    centerIdInput.value = entityId;
    includeAllCheckbox.checked = false;
    centerIdInput.disabled = false;
    entitySearchInput.disabled = false;
    loadGraph();
}

// Reset view - fit graph to window at 90% with centering
function resetView() {
    if (!simulation || currentData.nodes.length === 0) {
        // No graph loaded, just reset to identity
        svg.transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity);
        return;
    }
    
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Calculate bounding box of all nodes
    const nodes = simulation.nodes();
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    nodes.forEach(node => {
        if (node.x < minX) minX = node.x;
        if (node.x > maxX) maxX = node.x;
        if (node.y < minY) minY = node.y;
        if (node.y > maxY) maxY = node.y;
    });
    
    // Add padding for node radius and labels
    const padding = 50;
    minX -= padding;
    maxX += padding;
    minY -= padding;
    maxY += padding;
    
    const graphWidth = maxX - minX;
    const graphHeight = maxY - minY;
    
    // Calculate scale to fit graph in 90% of viewport
    const scaleX = (width * 0.9) / graphWidth;
    const scaleY = (height * 0.9) / graphHeight;
    const scale = Math.min(scaleX, scaleY, 2);  // Cap at 2x zoom
    
    // Calculate center of the graph
    const graphCenterX = (minX + maxX) / 2;
    const graphCenterY = (minY + maxY) / 2;
    
    // Calculate translation to center the graph
    const translateX = width / 2 - graphCenterX * scale;
    const translateY = height / 2 - graphCenterY * scale;
    
    // Apply transform with smooth transition
    const transform = d3.zoomIdentity
        .translate(translateX, translateY)
        .scale(scale);
    
    svg.transition()
        .duration(750)
        .call(zoom.transform, transform);
}

// Show loading state
function showLoading() {
    g.selectAll('*').remove();
    g.append('text')
        .attr('class', 'loading')
        .attr('x', '50%')
        .attr('y', '50%')
        .attr('text-anchor', 'middle')
        .attr('fill', '#888')
        .text('Loading...');
}

// Show error
function showError(message) {
    g.selectAll('*').remove();
    g.append('text')
        .attr('class', 'error-message')
        .attr('x', '50%')
        .attr('y', '50%')
        .attr('text-anchor', 'middle')
        .attr('fill', '#e94560')
        .text(message);
}
