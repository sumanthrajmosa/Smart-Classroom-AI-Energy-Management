import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, Camera, CheckCircle2, Clock3, LayoutDashboard,
  LockKeyhole, RefreshCw, ScanFace, ShieldCheck, Users,
  Video, Wifi, Image as ImageIcon,
} from 'lucide-react'
import {
  Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const REFRESH_MS = Number(import.meta.env.VITE_REFRESH_MS || 10000)
const API_KEY = import.meta.env.VITE_API_KEY || ''

const stages = [
  { id: 'input.jpg', title: 'Input Image', subtitle: 'Original classroom frame', icon: Camera },
  { id: 'detected.jpg', title: 'Face Detection', subtitle: 'InsightFace detections', icon: ScanFace },
  { id: 'anonymized.jpg', title: 'Face Anonymization', subtitle: 'Privacy transformation', icon: ShieldCheck },
  { id: 'zone_division.jpg', title: 'Zone Division', subtitle: 'Four-region occupancy', icon: LayoutDashboard },
  { id: 'classroom_result.jpg', title: 'Final Classroom Result', subtitle: 'Combined annotated output', icon: ImageIcon },
]

const zoneLabels = {
  BACK_LEFT: 'Back Left',
  BACK_RIGHT: 'Back Right',
  FRONT_LEFT: 'Front Left',
  FRONT_RIGHT: 'Front Right',
}

function App() {
  const [page, setPage] = useState('Overview')
  const [data, setData] = useState(null)
  const [images, setImages] = useState({})
  const [report, setReport] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)

  const headers = useMemo(() => API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {}, [])

  const getJSON = useCallback(async (path) => {
    const response = await fetch(`${API_BASE}${path}`, { headers, cache: 'no-store' })
    if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`)
    return response.json()
  }, [headers])

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const [dashboard, imageList, reportResponse] = await Promise.all([
        getJSON('/api/dashboard'),
        getJSON('/api/images'),
        fetch(`${API_BASE}/api/occupancy-report`, { headers, cache: 'no-store' }),
      ])
      if (!reportResponse.ok) throw new Error(`Occupancy report: HTTP ${reportResponse.status}`)
      const reportText = await reportResponse.text()
      const names = imageList.images || []
      const imageEntries = await Promise.all(names.map(async (name) => {
        const response = await fetch(`${API_BASE}/api/images/${encodeURIComponent(name)}?t=${Date.now()}`, { headers, cache: 'no-store' })
        if (!response.ok) return [name, null]
        return [name, URL.createObjectURL(await response.blob())]
      }))
      setImages((previous) => {
        Object.values(previous).forEach((url) => url && URL.revokeObjectURL(url))
        return Object.fromEntries(imageEntries)
      })
      setData(dashboard)
      setReport(reportText)
      setLastUpdated(new Date())
      setError('')
    } catch (err) {
      setError(err.message || 'Unable to connect to the backend')
    } finally {
      setLoading(false)
    }
  }, [getJSON, headers])

  useEffect(() => {
    refresh()
    const timer = window.setInterval(refresh, Math.max(3000, REFRESH_MS))
    return () => window.clearInterval(timer)
  }, [refresh])

  useEffect(() => () => {
    Object.values(images).forEach((url) => url && URL.revokeObjectURL(url))
  }, [images])

  const regions = data?.regions || {}
  const chartData = Object.entries(zoneLabels).map(([key, label]) => ({
    region: label,
    occupancy: Number(regions[key] || 0),
  }))
  const imageFor = (name) => images[name] || null

  function SidebarButton({ label, icon: Icon }) {
    return (
      <button className={`nav-item ${page === label ? 'active' : ''}`} onClick={() => setPage(label)}>
        <Icon size={18} /><span>{label}</span>
      </button>
    )
  }

  function Metric({ label, value, detail, icon: Icon }) {
    return (
      <article className="metric-card">
        <div className="metric-top"><span>{label}</span><span className="metric-icon"><Icon size={18} /></span></div>
        <strong>{value ?? '—'}</strong><small>{detail}</small>
      </article>
    )
  }

  function ImagePanel({ name, title, description }) {
    const src = imageFor(name)
    return (
      <article className="panel image-panel">
        <div className="panel-heading"><div><h3>{title}</h3><p>{description}</p></div><ImageIcon size={18} /></div>
        {src ? <img src={src} alt={title} /> : <div className="image-empty"><Camera size={28} /><span>{name} not available yet</span></div>}
      </article>
    )
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Activity size={22} /></div><div><b>SMART CLASSROOM</b><small>ENERGY MANAGEMENT</small></div></div>
        <div className="side-caption">WORKSPACE</div>
        <SidebarButton label="Overview" icon={LayoutDashboard} />
        <SidebarButton label="Face Detection" icon={ScanFace} />
        <SidebarButton label="Face Anonymization" icon={ShieldCheck} />
        <SidebarButton label="Zone Division" icon={LayoutDashboard} />
        <SidebarButton label="Final Result" icon={ImageIcon} />
        <SidebarButton label="Live Monitoring" icon={Video} />
        <div className="sidebar-footer"><LockKeyhole size={16} /><span>Privacy-first monitoring</span></div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div><div className="eyebrow">TEAM 107 · AMRITA VISHWA VIDYAPEETHAM</div><h1>{page}</h1></div>
          <div className="top-actions">
            <span className={`status-pill ${data ? 'online' : 'offline'}`}><span />{data ? 'API Connected' : 'API Disconnected'}</span>
            <button className="refresh-button" onClick={refresh} disabled={loading}><RefreshCw size={16} className={loading ? 'spin' : ''} /> Refresh</button>
          </div>
        </header>

        {error && <div className="error-banner"><Wifi size={17} /> {error}. Check the Raspberry Pi backend and API URL.</div>}

        {page === 'Overview' && <>
          <section className="welcome-row"><div><h2>Classroom occupancy overview</h2><p>Aggregated occupancy and anonymized processing outputs from the Raspberry Pi.</p></div><div className="updated"><Clock3 size={15} />{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : 'Waiting for data'}</div></section>
          <section className="metrics-grid">
            <Metric label="Total Occupancy" value={data?.total_occupancy ?? '—'} detail="Estimated from current report" icon={Users} />
            <Metric label="Active Regions" value={data ? `${data.active_regions || 0} / 4` : '—'} detail="Regions with detected occupancy" icon={LayoutDashboard} />
            <Metric label="Camera Status" value={data?.camera_status || '—'} detail="Based on final image availability" icon={Camera} />
            <Metric label="Processing Status" value={data?.processing_status || '—'} detail="Output directory status" icon={CheckCircle2} />
          </section>
          <section className="content-grid">
            <ImagePanel name="classroom_result.jpg" title="Final Classroom Result" description="Anonymized image with region annotations" />
            <article className="panel chart-panel"><div className="panel-heading"><div><h3>Region Distribution</h3><p>Estimated occupancy across four calibrated zones</p></div><Users size={18} /></div>
              <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData} margin={{ top: 12, right: 12, left: -18, bottom: 8 }}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e8edf3" /><XAxis dataKey="region" tick={{ fill: '#68758a', fontSize: 11 }} axisLine={false} tickLine={false} /><YAxis allowDecimals={false} tick={{ fill: '#68758a', fontSize: 11 }} axisLine={false} tickLine={false} /><Tooltip /><Bar dataKey="occupancy" name="Occupancy" fill="#3867d6" radius={[6, 6, 0, 0]} /></BarChart></ResponsiveContainer></div>
            </article>
          </section>
          <section className="panel"><div className="panel-heading"><div><h3>Processing pipeline</h3><p>Latest image outputs available from the Raspberry Pi</p></div></div><div className="stage-grid">{stages.map((stage) => <button className="stage-card" key={stage.id} onClick={() => setPage(stage.title === 'Final Classroom Result' ? 'Final Result' : stage.title)}><stage.icon size={18} /><b>{stage.title}</b><small>{stage.subtitle}</small><span>{imageFor(stage.id) ? 'Image available' : 'Waiting for output'}</span></button>)}</div></section>
        </>}

        {page === 'Face Detection' && <><section className="welcome-row"><div><h2>Face detection stage</h2><p>InsightFace detections visualized on the classroom input.</p></div></section><section className="content-grid"><ImagePanel name="input.jpg" title="Input Image" description="Classroom image supplied to the pipeline" /><ImagePanel name="detected.jpg" title="Detected Faces" description="Face bounding boxes and detection stage output" /></section></>}
        {page === 'Face Anonymization' && <><section className="welcome-row"><div><h2>Privacy transformation</h2><p>Detected face regions are transformed before dashboard display.</p></div></section><section className="content-grid"><ImagePanel name="detected.jpg" title="Detection Input" description="Face regions before anonymization" /><ImagePanel name="anonymized.jpg" title="Anonymized Output" description="Downsampling, blur, noise and smoothing" /></section></>}
        {page === 'Zone Division' && <><section className="welcome-row"><div><h2>Four-region occupancy</h2><p>Region assignment follows the calibration logic in the deployed processing code.</p></div></section><section className="content-grid"><ImagePanel name="anonymized.jpg" title="Anonymized Input" description="Image used for region analysis" /><ImagePanel name="zone_division.jpg" title="Zone Division" description="Four calibrated classroom regions" /></section><section className="panel zone-list">{chartData.map((zone) => <div key={zone.region}><span>{zone.region}</span><b>{zone.occupancy}</b></div>)}</section></>}
        {page === 'Final Result' && <><section className="welcome-row"><div><h2>Final annotated classroom image</h2><p>Combined anonymized image and occupancy visualization.</p></div></section><ImagePanel name="classroom_result.jpg" title="Final Classroom Result" description="Final output from the processing pipeline" /></>}
        {page === 'Live Monitoring' && <><section className="welcome-row"><div><h2>Live monitoring</h2><p>Dashboard refreshes at the configured interval; this is not a claim of continuous video inference.</p></div><div className="updated">Refresh: {REFRESH_MS / 1000}s</div></section><section className="metrics-grid"><Metric label="Total Occupancy" value={data?.total_occupancy ?? '—'} detail="Latest report" icon={Users} /><Metric label="API" value={data ? 'Connected' : 'Offline'} detail="Backend availability" icon={Wifi} /><Metric label="Active Regions" value={data ? `${data.active_regions || 0}/4` : '—'} detail="Current zone counts" icon={Activity} /><Metric label="Last Updated" value={lastUpdated?.toLocaleTimeString() || '—'} detail="Browser refresh time" icon={Clock3} /></section><section className="content-grid"><ImagePanel name="classroom_result.jpg" title="Current Classroom Image" description="Most recent final output file" /><article className="panel report-panel"><div className="panel-heading"><div><h3>Occupancy Report</h3><p>Text report generated by the image-processing pipeline</p></div></div><pre>{report || 'Waiting for occupancy report...'}</pre></article></section></>}

        <footer className="footer"><span>Optimized Sensor-Based Energy Efficient Smart Classroom</span><span>Raspberry Pi · FastAPI · React</span></footer>
      </main>
    </div>
  )
}

export default App
