import React, { useState, useEffect } from 'react'
import {
  Search,
  Building2,
  Package,
  TrendingUp,
  Globe,
  Copy,
  Check,
  X,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  AlertCircle,
  Plus
} from 'lucide-react'

const API_BASE = 'http://127.0.0.1:5000'

// Registry of known vendors with realistic Indian hubs and baseline metrics
const VENDOR_DIRECTORY = {
  "Apex Industrial Supplies": { region: "Pune, MH", onTimePct: "40%", avgPrice: "₹175/m", lastOrder: "PO-2041 · 02 Sep 2026", status: "amber", statusText: "10–15d delay risk" },
  "Apex Steel": { region: "Jamshedpur, JH", onTimePct: "100%", avgPrice: "₹190/kg", lastOrder: "PO-2045 · 29 Sep 2026", status: "good", statusText: "On schedule" },
  "Bharat Polymers": { region: "Mumbai, MH", onTimePct: "96%", avgPrice: "₹155/kg", lastOrder: "PO-2039 · 24 Aug 2026", status: "good", statusText: "WhatsApp active" },
  "Coastal Timber & Pallets": { region: "Mangalore, KA", onTimePct: "98%", avgPrice: "₹1,450/unit", lastOrder: "PO-2042 · 14 Sep 2026", status: "good", statusText: "On schedule" },
  "Delta Packaging": { region: "Surat, GJ", onTimePct: "95%", avgPrice: "₹35/box", lastOrder: "PO-2043 · 18 Sep 2026", status: "good", statusText: "Flexible on quote" },
  "Metro Steel & Wire": { region: "Bhilai, CG", onTimePct: "99%", avgPrice: "₹235/kg", lastOrder: "PO-2038 · 20 Aug 2026", status: "good", statusText: "On schedule" },
  "Orion Precision Alloys": { region: "Bengaluru, KA", onTimePct: "98%", avgPrice: "₹720/kg", lastOrder: "PO-2044 · 22 Sep 2026", status: "good", statusText: "ISO certified" },
  "Pioneer Plastics": { region: "Ahmedabad, GJ", onTimePct: "95%", avgPrice: "₹290/kg", lastOrder: "PO-2040 · 28 Aug 2026", status: "good", statusText: "On schedule" },
  "Summit Chemicals": { region: "Vadodara, GJ", onTimePct: "97%", avgPrice: "₹520/L", lastOrder: "PO-2041 · 10 Sep 2026", status: "good", statusText: "MSDS verified" },
  "Swift Electricals": { region: "Coimbatore, TN", onTimePct: "96%", avgPrice: "₹420/m", lastOrder: "PO-2037 · 11 Aug 2026", status: "good", statusText: "On schedule" },
  "Titan Fasteners": { region: "Chennai, TN", onTimePct: "60%", avgPrice: "₹12/unit", lastOrder: "PO-2040 · 06 Sep 2026", status: "amber", statusText: "Bulk delay (>5k)" },
  "Vanguard Tooling": { region: "Faridabad, HR", onTimePct: "97%", avgPrice: "₹1,850/unit", lastOrder: "PO-2044 · 25 Sep 2026", status: "good", statusText: "On schedule" },
  "Zenith Castings": { region: "Rajkot, GJ", onTimePct: "95%", avgPrice: "₹1,800/unit", lastOrder: "PO-2039 · 16 Aug 2026", status: "good", statusText: "Defect resolved" },
  // Marketplace network vendors
  "Kaveri Metals & Tubes": { region: "Pune, MH", onTimePct: "98%", avgPrice: "₹165/m", lastOrder: "New to buyer", status: "good", statusText: "Peer verified" },
  "Sterling Castings Ltd": { region: "Vadodara, GJ", onTimePct: "99%", avgPrice: "₹1,750/unit", lastOrder: "New to buyer", status: "good", statusText: "Peer verified" },
  "Nordic Fasteners Corp": { region: "Bengaluru, KA", onTimePct: "99%", avgPrice: "₹14/unit", lastOrder: "New to buyer", status: "good", statusText: "High volume OK" },
  "EcoBox Logistics Packaging": { region: "Ahmedabad, GJ", onTimePct: "96%", avgPrice: "₹32/box", lastOrder: "New to buyer", status: "good", statusText: "Peer verified" },
  "Solventex Industrial Solutions": { region: "Hyderabad, TS", onTimePct: "97%", avgPrice: "₹490/L", lastOrder: "New to buyer", status: "good", statusText: "Peer verified" },
  "Global Polymer Dynamics": { region: "Gurgaon, HR", onTimePct: "88%", avgPrice: "₹260/kg", lastOrder: "New to buyer", status: "amber", statusText: "High MOQ (1t)" }
}

const PRESET_QUERIES = [
  { label: "Steel tubing (line 2)", query: "I need 2,000 meters of structural steel tubing on a tight budget, but I cannot tolerate delivery delays for line 2." },
  { label: "M6 flange nuts (bulk)", query: "I need 25,000 units of M6 zinc-plated flange nuts urgently for full-scale production." },
  { label: "Aluminum valves (zero defect)", query: "Looking for 300 custom aluminum valve bodies. Hydrostatic pressure pass rate and zero porosity is critical." },
  { label: "Cartons (volume negotiation)", query: "Need 4,000 heavy-duty corrugated cartons. Want competitive rates and willing to cite competitor quotes." },
  { label: "LDPE film (urgent dispatch)", query: "Need 1,000 kg of LDPE film rolls ASAP. Who is the best contact person and how should I reach them?" }
]

export default function App() {
  const [activeNav, setActiveNav] = useState('sourcing') // 'sourcing' | 'vendors' | 'orders' | 'insights' | 'marketplace'
  
  // Sourcing State
  const [query, setQuery] = useState(PRESET_QUERIES[0].query)
  const [memoryOn, setMemoryOn] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [response, setResponse] = useState(null)
  const [expandedVendor, setExpandedVendor] = useState(null)
  const [copiedIndex, setCopiedIndex] = useState(null)

  // Drawer State
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [drawerVendor, setDrawerVendor] = useState(Object.keys(VENDOR_DIRECTORY)[0])
  const [drawerMaterial, setDrawerMaterial] = useState("")
  const [drawerRegion, setDrawerRegion] = useState("")
  const [drawerPrice, setDrawerPrice] = useState("")
  const [drawerDelay, setDrawerDelay] = useState(0)
  const [drawerQuality, setDrawerQuality] = useState("Good")
  const [drawerVerdict, setDrawerVerdict] = useState("")
  const [submittingOutcome, setSubmittingOutcome] = useState(false)
  const [outcomeSuccessMsg, setOutcomeSuccessMsg] = useState(null)
  const [outcomeErrorMsg, setOutcomeErrorMsg] = useState(null)

  // Insights State
  const [insights, setInsights] = useState("")
  const [loadingInsights, setLoadingInsights] = useState(false)
  const [insightsError, setInsightsError] = useState(null)
  const [insightsTimestamp, setInsightsTimestamp] = useState("29 Sep 2026, 14:15 IST")

  // Marketplace State
  const [marketplaceData, setMarketplaceData] = useState(null)
  const [loadingMarketplace, setLoadingMarketplace] = useState(false)

  // Recent order activity log (seeded for realism)
  const [ordersLog, setOrdersLog] = useState([
    { id: "PO-2045", date: "29 Sep 2026", vendor: "Apex Steel", material: "Carbon steel bar (500 units)", price: "₹190/kg", delay: "0d", quality: "Grade A", verdict: "On schedule, acceptable" },
    { id: "PO-2044", date: "25 Sep 2026", vendor: "Vanguard Tooling", material: "Carbide drills (80 units)", price: "₹1,850/pc", delay: "0d", quality: "Standard", verdict: "Delivered on schedule" },
    { id: "PO-2043", date: "18 Sep 2026", vendor: "Delta Packaging", material: "Corrugated cartons (4,000 units)", price: "₹34.50/pc", delay: "0d", quality: "Standard", verdict: "Matched competitor rate" },
    { id: "PO-2042", date: "14 Sep 2026", vendor: "Coastal Timber & Pallets", material: "Export crates (100 units)", price: "₹1,450/pc", delay: "0d", quality: "ISPM-15", verdict: "On schedule" },
    { id: "PO-2041", date: "02 Sep 2026", vendor: "Apex Industrial Supplies", material: "Black iron pipe (2,000m)", price: "₹175/m", delay: "15d late", quality: "Acceptable", verdict: "Cheapest, but 15-day delay halted line" }
  ])

  useEffect(() => {
    fetchInsights()
  }, [])

  const fetchInsights = async () => {
    setLoadingInsights(true)
    setInsightsError(null)
    try {
      const res = await fetch(`${API_BASE}/insights`)
      const raw = await res.text()
      const data = raw ? JSON.parse(raw) : {}
      if (res.ok && data.success) {
        setInsights(data.insights)
        setInsightsTimestamp(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' }))
      } else {
        setInsightsError(data.error || "Unable to fetch insights from Hindsight Cloud.")
      }
    } catch {
      setInsightsError("Cannot reach backend service at http://127.0.0.1:5000.")
    } finally {
      setLoadingInsights(false)
    }
  }

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResponse(null)
    setExpandedVendor(null)

    try {
      const res = await fetch(`${API_BASE}/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_text: query, memory_on: memoryOn })
      })

      const raw = await res.text()
      const data = raw ? JSON.parse(raw) : {}
      if (res.ok && data.success) {
        setResponse(data)
        if (data.vendors?.length > 0) {
          setExpandedVendor(0) // auto-expand top vendor
        }
      } else {
        setError(data.error || `Server error (${res.status}).`)
      }
    } catch {
      setError("Network error: Unable to contact backend on http://127.0.0.1:5000.")
    } finally {
      setLoading(false)
    }
  }

  const handleDiscover = async () => {
    setLoadingMarketplace(true)
    try {
      const res = await fetch(`${API_BASE}/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_text: query })
      })
      const raw = await res.text()
      const data = raw ? JSON.parse(raw) : {}
      if (res.ok && data.success) {
        setMarketplaceData(data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingMarketplace(false)
    }
  }

  const handleCopyMessage = (text, idx) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(idx)
    setTimeout(() => setCopiedIndex(null), 1800)
  }

  const openLogDrawerForVendor = (vendorName) => {
    setDrawerVendor(vendorName)
    setDrawerMaterial(query.slice(0, 45))
    setOutcomeSuccessMsg(null)
    setOutcomeErrorMsg(null)
    setIsDrawerOpen(true)
  }

  const handleSaveOutcome = async (e) => {
    e.preventDefault()
    setSubmittingOutcome(true)
    setOutcomeSuccessMsg(null)
    setOutcomeErrorMsg(null)

    const payload = {
      vendor: drawerVendor,
      material: drawerMaterial,
      price: drawerPrice,
      delay_days: Number(drawerDelay) || 0,
      quality: drawerQuality,
      region: drawerRegion || VENDOR_DIRECTORY[drawerVendor]?.region || "India",
      verdict: drawerVerdict
    }

    try {
      const res = await fetch(`${API_BASE}/outcome`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const raw = await res.text()
      const data = raw ? JSON.parse(raw) : {}
      if (res.ok && data.success) {
        setOutcomeSuccessMsg(data.retained_sentence)
        // Add to recent orders table for realism
        const newPo = `PO-${Math.floor(2050 + Math.random() * 50)}`
        setOrdersLog([
          {
            id: newPo,
            date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
            vendor: drawerVendor,
            material: drawerMaterial,
            price: drawerPrice || "Market",
            delay: Number(drawerDelay) > 0 ? `${drawerDelay}d late` : '0d',
            quality: drawerQuality,
            verdict: drawerVerdict || 'Recorded'
          },
          ...ordersLog
        ])
        setDrawerMaterial("")
        setDrawerPrice("")
        setDrawerDelay(0)
        setDrawerVerdict("")
      } else {
        setOutcomeErrorMsg(data.error || "Failed to record outcome in Hindsight.")
      }
    } catch {
      setOutcomeErrorMsg("Connection error: Unable to record outcome.")
    } finally {
      setSubmittingOutcome(false)
    }
  }

  const extractDateTag = (text = "") => {
    const match = text.match(/(?:April|May|June|July|August|September|\b2026\b|\b\d{4}-\d{2}-\d{2}\b)[^.,|]*/i)
    return match ? match[0].trim().slice(0, 15) : "2026"
  }

  const extractVendorTag = (text = "") => {
    for (const v of Object.keys(VENDOR_DIRECTORY)) {
      if (text.toLowerCase().includes(v.toLowerCase())) return v
    }
    return "Vendor"
  }

  return (
    <div className="app-shell">
      {/* 1. Fixed Left Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">S</div>
          <span className="sidebar-title">SourceMind</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className={`nav-item ${activeNav === 'sourcing' ? 'active' : ''}`}
            onClick={() => setActiveNav('sourcing')}
          >
            <Search />
            <span>Sourcing</span>
          </button>

          <button
            type="button"
            className={`nav-item ${activeNav === 'vendors' ? 'active' : ''}`}
            onClick={() => setActiveNav('vendors')}
          >
            <Building2 />
            <span>Vendors</span>
          </button>

          <button
            type="button"
            className={`nav-item ${activeNav === 'orders' ? 'active' : ''}`}
            onClick={() => setActiveNav('orders')}
          >
            <Package />
            <span>Orders</span>
          </button>

          <button
            type="button"
            className={`nav-item ${activeNav === 'insights' ? 'active' : ''}`}
            onClick={() => { setActiveNav('insights'); fetchInsights(); }}
          >
            <TrendingUp />
            <span>Insights</span>
          </button>

          <button
            type="button"
            className={`nav-item ${activeNav === 'marketplace' ? 'active' : ''}`}
            onClick={() => { setActiveNav('marketplace'); if (!marketplaceData) handleDiscover(); }}
          >
            <Globe />
            <span>Marketplace</span>
          </button>
        </nav>

        <div className="sidebar-footer">
          <div>Memory Bank:</div>
          <div className="bank-tag">
            <span className="bank-dot"></span>
            <span>buyer1 (Active)</span>
          </div>
        </div>
      </aside>

      {/* 2. Main Layout Container */}
      <div className="main-layout">
        {/* Central Content Area */}
        <main className="content-area">
          {/* Header Bar */}
          <div className="page-header">
            <div>
              <h1 className="page-title">
                {activeNav === 'sourcing' && "Vendor Sourcing"}
                {activeNav === 'vendors' && "Approved Vendor Directory"}
                {activeNav === 'orders' && "Historical Purchase Orders"}
                {activeNav === 'insights' && "Procurement Intelligence"}
                {activeNav === 'marketplace' && "Marketplace Network"}
              </h1>
            </div>

            <div className="page-actions">
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setIsDrawerOpen(true)}
              >
                <Plus size={14} />
                <span>Log outcome</span>
              </button>
            </div>
          </div>

          {/* VIEW: SOURCING (MAIN) */}
          {activeNav === 'sourcing' && (
            <div>
              {/* Request Field Bar */}
              <div className="request-card">
                <form onSubmit={handleSearch}>
                  <div className="request-input-row">
                    <input
                      type="text"
                      className="input-field"
                      placeholder="Specify material specifications, quantity, and lead time requirement..."
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                    />
                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={loading || !query.trim()}
                    >
                      {loading ? (
                        <>
                          <RefreshCw size={14} className="spinner" />
                          <span>Searching...</span>
                        </>
                      ) : (
                        <span>Find vendors</span>
                      )}
                    </button>
                  </div>

                  <div className="request-controls">
                    <div className="preset-group">
                      <span className="preset-label">Quick spec:</span>
                      {PRESET_QUERIES.map((p, idx) => (
                        <button
                          key={idx}
                          type="button"
                          className="preset-btn"
                          onClick={() => setQuery(p.query)}
                        >
                          {p.label}
                        </button>
                      ))}
                    </div>

                    <div className="memory-switch-wrapper">
                      <label className="switch-toggle">
                        <input
                          type="checkbox"
                          checked={memoryOn}
                          onChange={(e) => setMemoryOn(e.target.checked)}
                        />
                        <span className="switch-slider"></span>
                      </label>
                      <span className="switch-label">
                        Use vendor memory
                      </span>
                    </div>
                  </div>
                </form>
              </div>

              {/* Error Notice */}
              {error && (
                <div className="alert-box error" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
                  <AlertCircle size={16} />
                  <span>{error}</span>
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    style={{ marginLeft: 'auto' }}
                    onClick={handleSearch}
                  >
                    Retry
                  </button>
                </div>
              )}

              {/* Loading Skeletons */}
              {loading && (
                <div className="table-panel">
                  <div className="table-header-bar">
                    <span className="table-header-title">Ranking candidates from memory...</span>
                  </div>
                  {[1, 2, 3].map((n) => (
                    <div key={n} className="skeleton-row">
                      <div className="skeleton-bar" style={{ width: '100%' }}></div>
                    </div>
                  ))}
                </div>
              )}

              {/* Results Display */}
              {!loading && response && (
                <div>
                  {/* Analysis Strip */}
                  {response.analysis && (
                    <div className="analysis-strip">
                      <strong>Executive assessment: </strong>
                      <span>{response.analysis}</span>
                    </div>
                  )}

                  {/* Vendor Table */}
                  <div className="table-panel">
                    <div className="table-header-bar">
                      <span className="table-header-title">Recommended Vendors</span>
                      <span className="table-header-meta">
                        {response.vendors?.length || 0} candidate(s) evaluated
                      </span>
                    </div>

                    <table className="data-table">
                      <thead>
                        <tr>
                          <th style={{ width: '45px' }}>Rank</th>
                          <th>Vendor</th>
                          <th>Region</th>
                          <th>On-time %</th>
                          <th>Avg price (₹/kg)</th>
                          <th>Last order</th>
                          <th>Score</th>
                          <th style={{ textAlign: 'right' }}>Why</th>
                        </tr>
                      </thead>
                      <tbody>
                        {response.vendors?.map((v, idx) => {
                          const meta = VENDOR_DIRECTORY[v.name] || {
                            region: "India",
                            onTimePct: "95%",
                            avgPrice: v.price_assessment || "Market",
                            lastOrder: "PO-2045",
                            status: "good",
                            statusText: v.risk_assessment || "Standard"
                          }
                          const isExpanded = expandedVendor === idx
                          const vendorScore = v.score || (idx === 0 ? "9.6" : idx === 1 ? "8.9" : idx === 2 ? "8.1" : "7.4")

                          return (
                            <React.Fragment key={idx}>
                              <tr
                                className={isExpanded ? 'expanded-row' : ''}
                                style={{ cursor: 'pointer' }}
                                onClick={() => setExpandedVendor(isExpanded ? null : idx)}
                              >
                                <td className="tabular" style={{ color: 'var(--text-muted)', fontWeight: 600 }}>
                                  #{v.rank || idx + 1}
                                </td>
                                <td>
                                  <strong>{v.name}</strong>
                                </td>
                                <td style={{ color: 'var(--text-muted)' }}>
                                  {meta.region}
                                </td>
                                <td className="tabular">
                                  {meta.onTimePct}
                                </td>
                                <td className="tabular">
                                  {meta.avgPrice}
                                </td>
                                <td className="tabular" style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                                  {meta.lastOrder}
                                </td>
                                <td>
                                  <span className={`status-pill ${meta.status}`}>
                                    <span className="tabular" style={{ fontWeight: 600 }}>{vendorScore}</span>
                                    <span>· {meta.statusText}</span>
                                  </span>
                                </td>
                                <td style={{ textAlign: 'right' }}>
                                  <button
                                    type="button"
                                    className="why-link"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      setExpandedVendor(isExpanded ? null : idx)
                                    }}
                                  >
                                    <span>{isExpanded ? "Close" : "Why"}</span>
                                    {isExpanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                                  </button>
                                </td>
                              </tr>

                              {/* Expanded Row Content */}
                              {isExpanded && (
                                <tr>
                                  <td colSpan={8} style={{ padding: 0 }}>
                                    <div className="row-detail-box">
                                      <div>
                                        <div className="detail-section-title">Historical Reasoning & Justification</div>
                                        <p className="reason-text">{v.reason}</p>
                                        <div style={{ marginTop: '12px' }}>
                                          <button
                                            type="button"
                                            className="btn btn-secondary btn-sm"
                                            onClick={() => openLogDrawerForVendor(v.name)}
                                          >
                                            <Plus size={12} />
                                            <span>Record order outcome for {v.name}</span>
                                          </button>
                                        </div>
                                      </div>

                                      <div>
                                        <div className="detail-section-title">Drafted Procurement Outreach</div>
                                        <div className="draft-box">
                                          <div className="draft-content">
                                            {v.drafted_message}
                                          </div>
                                          <div className="draft-actions">
                                            <button
                                              type="button"
                                              className="btn btn-secondary btn-sm"
                                              onClick={() => handleCopyMessage(v.drafted_message, idx)}
                                            >
                                              {copiedIndex === idx ? (
                                                <>
                                                  <Check size={12} color="#166534" />
                                                  <span style={{ color: '#166534' }}>Copied</span>
                                                </>
                                              ) : (
                                                <>
                                                  <Copy size={12} />
                                                  <span>Copy message</span>
                                                </>
                                              )}
                                            </button>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </td>
                                </tr>
                              )}
                            </React.Fragment>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Initial Empty State */}
              {!loading && !response && (
                <div className="table-panel">
                  <div className="empty-state">
                    Enter required material specs above and select "Find vendors" to run memory-grounded supplier evaluation.
                  </div>
                </div>
              )}
            </div>
          )}

          {/* VIEW: VENDORS */}
          {activeNav === 'vendors' && (
            <div className="table-panel">
              <div className="table-header-bar">
                <span className="table-header-title">Approved Supplier Registry</span>
                <span className="table-header-meta">13 private vendors registered</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Vendor Name</th>
                    <th>Hub / State</th>
                    <th>On-time %</th>
                    <th>Standard Rate</th>
                    <th>Status Notes</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(VENDOR_DIRECTORY).slice(0, 13).map(([vName, vData], i) => (
                    <tr key={i}>
                      <td><strong>{vName}</strong></td>
                      <td style={{ color: 'var(--text-muted)' }}>{vData.region}</td>
                      <td className="tabular">{vData.onTimePct}</td>
                      <td className="tabular">{vData.avgPrice}</td>
                      <td>
                        <span className={`status-pill ${vData.status}`}>
                          {vData.statusText}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => openLogDrawerForVendor(vName)}
                        >
                          Log PO
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* VIEW: ORDERS */}
          {activeNav === 'orders' && (
            <div className="table-panel">
              <div className="table-header-bar">
                <span className="table-header-title">Purchase Order Log</span>
                <span className="table-header-meta">{ordersLog.length} recent executions</span>
              </div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>PO Ref</th>
                    <th>Date</th>
                    <th>Vendor</th>
                    <th>Material</th>
                    <th>Rate</th>
                    <th>Delay</th>
                    <th>Quality</th>
                    <th>Buyer Verdict</th>
                  </tr>
                </thead>
                <tbody>
                  {ordersLog.map((order, i) => (
                    <tr key={i}>
                      <td className="tabular" style={{ fontWeight: 600 }}>{order.id}</td>
                      <td className="tabular" style={{ color: 'var(--text-muted)' }}>{order.date}</td>
                      <td><strong>{order.vendor}</strong></td>
                      <td>{order.material}</td>
                      <td className="tabular">{order.price}</td>
                      <td>
                        <span className={`status-pill ${order.delay.includes('late') ? 'amber' : 'good'}`}>
                          {order.delay}
                        </span>
                      </td>
                      <td>{order.quality}</td>
                      <td style={{ color: 'var(--text-muted)' }}>{order.verdict}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* VIEW: INSIGHTS */}
          {activeNav === 'insights' && (
            <div className="table-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div>
                  <h2 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-main)' }}>
                    Patterns learned from your orders
                  </h2>
                  <div style={{ fontSize: '12px', color: 'var(--text-subtle)', marginTop: '2px' }}>
                    Last updated: {insightsTimestamp} · Synthesized across 42 order events via Hindsight reflect
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={fetchInsights}
                  disabled={loadingInsights}
                >
                  <RefreshCw size={12} className={loadingInsights ? "spinner" : ""} />
                  <span>Refresh</span>
                </button>
              </div>

              {loadingInsights ? (
                <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Reflecting on vendor performance & priorities...
                </div>
              ) : insightsError ? (
                <div className="alert-box error">{insightsError}</div>
              ) : (
                <div style={{ fontSize: '13px', lineHeight: 1.65, color: 'var(--text-body)' }}>
                  {insights ? (
                    insights
                      .split(/\n\s*\n/)
                      .filter((p) => p.trim().length > 0)
                      .map((para, idx) => (
                        <p key={idx} style={{ marginBottom: '14px' }}>
                          {para.trim()}
                        </p>
                      ))
                  ) : (
                    <p style={{ color: 'var(--text-muted)' }}>No patterns synthesized yet.</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* VIEW: MARKETPLACE */}
          {activeNav === 'marketplace' && (
            <div className="table-panel">
              <div className="table-header-bar">
                <div>
                  <span className="table-header-title">New vendors from the network</span>
                  <span className="status-pill good" style={{ marginLeft: '8px', fontSize: '10px' }}>
                    Sample data
                  </span>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleDiscover}
                  disabled={loadingMarketplace}
                >
                  <RefreshCw size={12} className={loadingMarketplace ? "spinner" : ""} />
                  <span>Discover suppliers</span>
                </button>
              </div>

              {loadingMarketplace && (
                <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Querying marketplace peer reviews from Hindsight Cloud...
                </div>
              )}

              {!loadingMarketplace && (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Candidate Vendor</th>
                      <th>Location</th>
                      <th>Strengths</th>
                      <th>Reviews Behind Suggestion</th>
                      <th style={{ textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marketplaceData?.suggestions && marketplaceData.suggestions.length > 0 ? (
                      marketplaceData.suggestions.map((s, idx) => (
                        <tr key={idx}>
                          <td><strong>{s.name}</strong></td>
                          <td style={{ color: 'var(--text-muted)' }}>{s.location || VENDOR_DIRECTORY[s.name]?.region || "India"}</td>
                          <td>
                            <span className="status-pill good">
                              {s.key_strengths || "Verified performance"}
                            </span>
                          </td>
                          <td style={{ maxWidth: '340px', fontSize: '12px', color: 'var(--text-muted)' }}>
                            {s.evidence?.[0] ? `"${s.evidence[0]}"` : s.reason_worth_trying}
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <button
                              type="button"
                              className="btn btn-secondary btn-sm"
                              onClick={() => openLogDrawerForVendor(s.name)}
                            >
                              Log trial order
                            </button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      // Default realistic marketplace network preview
                      [
                        { name: "Kaveri Metals & Tubes", loc: "Pune, MH", adv: "Fast 4-day dispatch, 8% below market", review: "Ramesh Sharma (Shanti Engineering): Ordered 1,500m tubing, exact tolerances, 4-day delivery." },
                        { name: "Nordic Fasteners Corp", loc: "Bengaluru, KA", adv: "Zero bottleneck on 50k+ bulk lots", review: "Vikram Mehta (Apex Auto): Delivered 50,000 bulk M8 bolts in 6 days with zero defects." },
                        { name: "Sterling Castings Ltd", loc: "Vadodara, GJ", adv: "100% hydrostatic pass rate", review: "Anita Desai (Precision Valves): 500 valve bodies delivered with zero porosity defects." },
                        { name: "EcoBox Logistics Packaging", loc: "Ahmedabad, GJ", adv: "250 PSI burst strength certified", review: "Deepak Patel (Western Pack): Competitive volume packaging delivered strictly on schedule." },
                        { name: "Solventex Industrial Solutions", loc: "Hyderabad, TS", adv: "Dedicated transport tanker fleet", review: "Kavita Reddy (Deccan Chem): High chemical purity cutting fluids and lubricants on schedule." }
                      ].map((item, i) => (
                        <tr key={i}>
                          <td><strong>{item.name}</strong></td>
                          <td style={{ color: 'var(--text-muted)' }}>{item.loc}</td>
                          <td>
                            <span className="status-pill good">{item.adv}</span>
                          </td>
                          <td style={{ maxWidth: '340px', fontSize: '12px', color: 'var(--text-muted)' }}>
                            "{item.review}"
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <button
                              type="button"
                              className="btn btn-secondary btn-sm"
                              onClick={() => openLogDrawerForVendor(item.name)}
                            >
                              Log trial order
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </main>

        {/* 3. Right Evidence Panel */}
        <aside className="evidence-panel">
          <div className="evidence-header">
            <div className="evidence-title">What the agent remembered</div>
            <div className="evidence-sub">
              {response?.memories_used?.length
                ? `${response.memories_used.length} memory events recalled from Hindsight`
                : "Contextual audit trail"}
            </div>
          </div>

          <div className="evidence-list">
            {!memoryOn ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '12px', lineHeight: 1.5 }}>
                Memory switch is toggled off. The agent is generating baseline heuristics without access to past vendor order histories.
              </div>
            ) : !response ? (
              <div style={{ color: 'var(--text-subtle)', fontSize: '12px' }}>
                Run a sourcing inquiry to view the exact historical interaction memories that ground the recommendation.
              </div>
            ) : response.memories_used?.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>
                No prior memory items matched this specific inquiry.
              </div>
            ) : (
              response.memories_used.slice(0, 8).map((mem, idx) => (
                <div key={idx} className="evidence-row">
                  <div>{mem}</div>
                  <div className="evidence-meta">
                    <span className="evidence-tag">{extractVendorTag(mem)}</span>
                    <span className="tabular">{extractDateTag(mem)}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>
      </div>

      {/* 4. Slide-over Drawer for Log Outcome */}
      {isDrawerOpen && (
        <div className="drawer-backdrop" onClick={() => setIsDrawerOpen(false)}>
          <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <span className="drawer-title">Log Order Outcome</span>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setIsDrawerOpen(false)}
              >
                <X size={14} />
              </button>
            </div>

            <form onSubmit={handleSaveOutcome} style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
              <div className="drawer-body">
                <div className="form-group">
                  <label className="form-label">Vendor</label>
                  <select
                    className="input-field"
                    value={drawerVendor}
                    onChange={(e) => setDrawerVendor(e.target.value)}
                  >
                    {Object.keys(VENDOR_DIRECTORY).map((v, i) => (
                      <option key={i} value={v}>{v}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Material / Description</label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g. Structural steel tubing (2,000m)"
                    value={drawerMaterial}
                    onChange={(e) => setDrawerMaterial(e.target.value)}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Region / Hub</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="e.g. Pune, MH"
                      value={drawerRegion}
                      onChange={(e) => setDrawerRegion(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Agreed Price</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="e.g. ₹175/m"
                      value={drawerPrice}
                      onChange={(e) => setDrawerPrice(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Delay (Days)</label>
                    <input
                      type="number"
                      min="0"
                      className="input-field"
                      placeholder="0 = on time"
                      value={drawerDelay}
                      onChange={(e) => setDrawerDelay(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Quality</label>
                    <select
                      className="input-field"
                      value={drawerQuality}
                      onChange={(e) => setDrawerQuality(e.target.value)}
                    >
                      <option value="Grade A">Grade A (Flawless)</option>
                      <option value="Good">Good / Standard</option>
                      <option value="Acceptable">Acceptable</option>
                      <option value="Defective">Defective / Rejected</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Buyer Verdict</label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g. Delivered 4 days late, halted line 2. Cheap but too risky."
                    value={drawerVerdict}
                    onChange={(e) => setDrawerVerdict(e.target.value)}
                  />
                </div>

                {outcomeSuccessMsg && (
                  <div className="alert-box success">
                    Saved to Hindsight memory: "{outcomeSuccessMsg}"
                  </div>
                )}
                {outcomeErrorMsg && (
                  <div className="alert-box error">
                    {outcomeErrorMsg}
                  </div>
                )}
              </div>

              <div className="drawer-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsDrawerOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submittingOutcome || !drawerMaterial.trim()}
                >
                  {submittingOutcome ? "Saving..." : "Log outcome"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
