import { useState } from 'react'
import { Routes, Route, Navigate, Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Factory, LayoutDashboard, CalendarDays, Cpu, Users, PackageOpen, Truck, ClipboardList,
  Bell, LogOut, AlertTriangle, Settings2, Flag, CalendarClock, UserCheck, Boxes, TimerOff, Banknote
} from 'lucide-react'

/* ---------------------------------------------------------
   BASE DATA
--------------------------------------------------------- */
const machines = [
  { id:'M1', name:'CNC Milling', status:'RUNNING', order:'O101', utilization:91, operation:'Milling', remaining:'42 min' },
  { id:'M2', name:'CNC Turning', status:'RUNNING', order:'O102', utilization:84, operation:'Turning', remaining:'68 min' },
  { id:'M3', name:'Assembly Line', status:'IDLE', order:'O103', utilization:77, operation:'Assembly', remaining:'—' },
  { id:'M4', name:'Packaging Unit', status:'RUNNING', order:'O104', utilization:88, operation:'Packaging', remaining:'25 min' },
]
const workers = [
  { id:'W01', name:'Arun Kumar', skill:'CNC Operator', machine:'M1', order:'O101', status:'WORKING', shift:'08:00–16:00', hours:6.4, certified:['M1','M2'] },
  { id:'W02', name:'Priya S', skill:'CNC Operator', machine:'M2', order:'O102', status:'WORKING', shift:'08:00–16:00', hours:6.1, certified:['M1','M2'] },
  { id:'W03', name:'Karthik R', skill:'Assembly Technician', machine:'M3', order:'O103', status:'AVAILABLE', shift:'08:00–16:00', hours:5.7, certified:['M3'] },
  { id:'W04', name:'Meena P', skill:'Packaging Operator', machine:'M4', order:'O104', status:'WORKING', shift:'08:00–16:00', hours:6.8, certified:['M4'] },
]
const orders = [
  { id:'O101', product:'Precision Housing', qty:120, priority:'HIGH', deadline:'Today 14:30', process:90, setup:15, machine:'M1', status:'IN PROGRESS', material:'Aluminum Billet' },
  { id:'O102', product:'Drive Shaft', qty:80, priority:'MEDIUM', deadline:'Today 15:30', process:120, setup:20, machine:'M2', status:'SCHEDULED', material:'Steel Rod' },
  { id:'O103', product:'Control Panel', qty:60, priority:'HIGH', deadline:'Today 13:45', process:75, setup:10, machine:'M3', status:'AT RISK', material:'Control Chips' },
  { id:'O104', product:'Packaged Unit', qty:200, priority:'LOW', deadline:'Today 16:00', process:60, setup:12, machine:'M4', status:'SCHEDULED', material:'Cardboard Packaging' },
]
const materials = [
  { id:'Steel Rod', stock:'Sufficient', risk:false },
  { id:'Control Chips', stock:'Delayed shipment — affects O103', risk:true },
  { id:'Aluminum Billet', stock:'Sufficient', risk:false },
  { id:'Cardboard Packaging', stock:'Sufficient', risk:false },
]
const nav = [
  ['/home','Dashboard',LayoutDashboard], ['/schedule','Production Schedule',CalendarDays], ['/orders','Orders',ClipboardList],
  ['/machines','Machines',Cpu], ['/workers','Workers',Users], ['/imports','Import Details',PackageOpen], ['/exports','Export Details',Truck]
]

/* ---------------------------------------------------------
   SCHEDULE SCENARIOS — original + two alternative reschedules
   Grid columns represent hours 08:00 → 18:00 (10 one-hour slots)
--------------------------------------------------------- */
const HOURS = ['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00']

const scenarios = {
  original: {
    label: 'Previous Schedule',
    tag: null,
    machineStatus: { M1:'RUNNING', M2:'RUNNING', M3:'IDLE', M4:'RUNNING' },
    blocks: { M1:[{o:'O101',s:0,l:3}], M2:[{o:'O102',s:1,l:3}], M3:[{o:'O103',s:0,l:5}], M4:[{o:'O104',s:2,l:4}] },
    kpis: { onTime:92, util:86, cost:48250, downtime:0, disruptions:0 },
    constraints: {
      machineAvail: '4 / 4 machines running',
      processing: 'Avg 86 min run + 14 min setup',
      priority: 'HIGH 2 · MEDIUM 1 · LOW 1',
      deadlines: 'Nearest: O103 @ 13:45',
      workforce: '4 / 4 workers assigned — all certified matches',
      material: 'Control Chips shipment delayed — O103 at risk',
      downtime: '0 min',
      cost: '₹48,250',
    },
    note: 'Baseline schedule — no active disruption.',
  },
  altA: {
    label: 'Alt A · Reassign to M1',
    tag: 'Minimize delay',
    machineStatus: { M1:'RUNNING', M2:'FAULT', M3:'IDLE', M4:'RUNNING' },
    blocks: { M1:[{o:'O101',s:0,l:3},{o:'O102',s:3,l:3}], M2:[], M3:[{o:'O103',s:0,l:5}], M4:[{o:'O104',s:2,l:4}] },
    kpis: { onTime:85, util:78, cost:51900, downtime:120, disruptions:1 },
    constraints: {
      machineAvail: '3 / 4 machines running (M2 fault)',
      processing: '+20 min setup to retool M1 for turning',
      priority: 'HIGH 2 · MEDIUM 1 · LOW 1 (unchanged)',
      deadlines: 'O102 still meets 15:30 deadline (finishes 14:00)',
      workforce: 'Priya S (certified on M1 & M2) reassigned to M1',
      material: 'Control Chips still delayed — unrelated to this change',
      downtime: '120 min (M2)',
      cost: '₹51,900 (+₹3,650)',
    },
    note: 'M2 failed. O102 reassigned to M1 — shares compatible CNC tooling and Priya S is certified on both machines. Delay is cut sharply, at the cost of retooling and a higher production cost.',
  },
  altB: {
    label: 'Alt B · Wait for Repair',
    tag: 'Minimize cost',
    machineStatus: { M1:'RUNNING', M2:'FAULT', M3:'IDLE', M4:'RUNNING' },
    blocks: { M1:[{o:'O101',s:0,l:3}], M2:[{o:'O102',s:6,l:3}], M3:[{o:'O103',s:0,l:5}], M4:[{o:'O104',s:2,l:4}] },
    kpis: { onTime:71, util:68, cost:49050, downtime:300, disruptions:1 },
    constraints: {
      machineAvail: '3 / 4 machines running (M2 fault)',
      processing: 'No retooling needed — same machine, same setup',
      priority: 'HIGH 2 · MEDIUM 1 · LOW 1 (unchanged)',
      deadlines: 'O102 now at risk against the 15:30 deadline',
      workforce: 'Priya S idle until M2 is restored',
      material: 'Control Chips still delayed — unrelated to this change',
      downtime: '300 min (M2)',
      cost: '₹49,050 (+₹800)',
    },
    note: 'O102 is held on M2 until the machine is repaired rather than reassigned. Minimal added cost, but the machine and its operator sit idle far longer and the delivery deadline is put at risk.',
  },
}

const constraintMeta = [
  ['machineAvail', 'Machine Availability', Cpu],
  ['processing', 'Processing & Setup Time', Settings2],
  ['priority', 'Order Priority', Flag],
  ['deadlines', 'Delivery Deadlines', CalendarClock],
  ['workforce', 'Workforce Availability', UserCheck],
  ['material', 'Material Constraints', Boxes],
  ['downtime', 'Downtime', TimerOff],
  ['cost', 'Production Cost', Banknote],
]

/* ---------------------------------------------------------
   SHARED UI
--------------------------------------------------------- */
function Badge({children}) {
  const cls = String(children).includes('FAULT') || String(children).includes('DELAY') || String(children).includes('AT RISK') ? 'bg-red-50 text-red-700' :
    String(children).includes('RUNNING') || String(children).includes('WORKING') || String(children).includes('DISPATCHED') ? 'bg-emerald-50 text-emerald-700' :
    String(children).includes('HIGH') ? 'bg-orange-50 text-orange-700' : 'bg-slate-100 text-slate-700'
  return <span className={`px-2 py-1 rounded-md text-xs font-semibold ${cls}`}>{children}</span>
}
function Layout({children}) {
  const loc=useLocation(), navg=useNavigate()
  return <div className="min-h-screen flex">
    <aside className="w-64 bg-slate-950 text-white p-4 hidden md:block">
      <div className="flex items-center gap-3 px-2 py-4 mb-4"><Factory/><div><div className="font-bold">SmartSched AI</div><div className="text-xs text-slate-400">Smart Factory Control</div></div></div>
      <nav className="space-y-1">{nav.map(([to,label,Icon])=><Link key={to} to={to} className={`flex items-center gap-3 px-3 py-3 rounded-lg text-sm ${loc.pathname===to?'bg-slate-800':'text-slate-300 hover:bg-slate-900'}`}><Icon size={18}/>{label}</Link>)}</nav>
      <div className="mt-8 border-t border-slate-800 pt-4"><button onClick={()=>navg('/login')} className="flex gap-3 items-center px-3 py-3 text-sm text-slate-300"><LogOut size={18}/>Logout</button></div>
    </aside>
    <main className="flex-1">
      <header className="h-16 bg-white border-b flex items-center justify-between px-5"><div className="font-semibold">{nav.find(x=>x[0]===loc.pathname)?.[1] || 'SmartSched AI'}</div><div className="flex items-center gap-4 text-sm"><span className="text-emerald-600">● Factory Online</span><Bell size={18}/><span className="font-medium">Operator</span></div></header>
      <div className="p-5 max-w-7xl mx-auto">{children}</div>
    </main>
  </div>
}
function Login(){
 const navg=useNavigate(); const [email,setEmail]=useState('demo@smartsched.ai'); const [pass,setPass]=useState('demo123'); const [err,setErr]=useState('')
 const submit=e=>{e.preventDefault(); if(!email||!pass){setErr('Enter email and password');return} navg('/home')}
 return <div className="min-h-screen grid place-items-center bg-slate-950 p-5"><form onSubmit={submit} className="bg-white w-full max-w-md rounded-2xl p-8 shadow-xl"><div className="flex items-center gap-3 mb-7"><Factory/><div><h1 className="text-xl font-bold">SmartSched AI</h1><p className="text-sm text-slate-500">Intelligent Production Scheduling</p></div></div><label className="text-sm font-medium">Email</label><input value={email} onChange={e=>setEmail(e.target.value)} className="w-full border rounded-lg p-3 mt-1 mb-4" type="email"/><label className="text-sm font-medium">Password</label><input value={pass} onChange={e=>setPass(e.target.value)} className="w-full border rounded-lg p-3 mt-1 mb-4" type="password"/>{err&&<p className="text-red-600 text-sm mb-3">{err}</p>}<button className="w-full bg-slate-900 text-white p-3 rounded-lg font-semibold">Login</button><button type="button" onClick={()=>{setEmail('demo@smartsched.ai');setPass('demo123')}} className="w-full mt-3 border p-3 rounded-lg">Demo Login</button></form></div>
}
function Home(){
 const [disrupt,setDisrupt]=useState(false)
 return <><div className="mb-5"><h1 className="text-2xl font-bold">Factory Operations Dashboard</h1><p className="text-slate-500">Real-time production overview and adaptive scheduling</p></div>
 <div className="grid grid-cols-2 lg:grid-cols-6 gap-3">{[['Active Orders','24'],['On-Time Delivery','92%'],['Machine Utilization','86%'],['Available Workers','18'],['Production Cost','₹48,250'],['Active Disruptions',disrupt?'1':'0']].map(x=><div className="bg-white border rounded-xl p-4" key={x[0]}><p className="text-xs text-slate-500">{x[0]}</p><p className="text-2xl font-bold mt-2">{x[1]}</p></div>)}</div>
 <div className="grid lg:grid-cols-3 gap-5 mt-5"><div className="lg:col-span-2 bg-white border rounded-xl"><div className="p-4 border-b font-semibold">Machine Overview</div><div className="divide-y">{machines.map(m=><div className="p-4 flex items-center justify-between" key={m.id}><div><b>{m.id} · {m.name}</b><div className="text-sm text-slate-500">{m.operation} · {m.remaining}</div></div><div className="flex items-center gap-5"><span>{m.utilization}%</span><Badge>{disrupt&&m.id==='M2'?'FAULT':m.status}</Badge></div></div>)}</div></div>
 <div className="bg-white border rounded-xl p-4"><div className="font-semibold mb-3">AI Insight</div><div className="bg-slate-50 rounded-lg p-4 text-sm"><b>Schedule Adaptation Recommended</b><p className="mt-2 text-slate-600">{disrupt?'M2 became unavailable. See the Production Schedule page for the two alternative reschedule options.':'No active disruption. Schedule is currently stable.'}</p></div><Link to="/schedule" onClick={()=>setDisrupt(true)} className="mt-4 block text-center w-full bg-slate-900 text-white p-2.5 rounded-lg">Simulate M2 Failure → View Schedule</Link></div></div></>
}
function TablePage({title,rows,columns}){return <div><h1 className="text-2xl font-bold mb-1">{title}</h1><p className="text-slate-500 mb-5">Operational data and current factory state</p><div className="bg-white border rounded-xl overflow-x-auto"><table className="w-full text-sm"><thead className="bg-slate-50"><tr>{columns.map(c=><th className="text-left p-3 font-semibold whitespace-nowrap" key={c}>{c}</th>)}</tr></thead><tbody className="divide-y">{rows.map((r,i)=><tr key={i}>{columns.map(c=><td className="p-3 whitespace-nowrap" key={c}>{r[c] ?? '—'}</td>)}</tr>)}</tbody></table></div></div>}

/* ---------------------------------------------------------
   CONSTRAINTS STRIP — all 8 PS parameters, live per scenario
--------------------------------------------------------- */
function ConstraintsStrip({scenario}) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
      {constraintMeta.map(([key,label,Icon]) => (
        <div key={key} className="bg-white border rounded-xl p-3">
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-1"><Icon size={14}/>{label}</div>
          <div className="text-sm font-medium leading-snug">{scenario.constraints[key]}</div>
        </div>
      ))}
    </div>
  )
}

/* ---------------------------------------------------------
   GANTT — renders a scenario's blocks across 10 hour columns
--------------------------------------------------------- */
function Gantt({scenario}) {
  return (
    <div className="bg-white border rounded-xl overflow-x-auto">
      <div className="min-w-[980px] p-4">
        <div className="grid grid-cols-11 text-xs text-slate-500 mb-3">
          <div>Machine</div>
          {HOURS.map(t=><div key={t}>{t}</div>)}
        </div>
        {machines.map(m => {
          const blocks = scenario.blocks[m.id] || []
          const status = scenario.machineStatus[m.id]
          return (
            <div className="grid grid-cols-11 items-center border-t min-h-16 relative" key={m.id}>
              <div className="font-semibold flex items-center gap-2">{m.id}<Badge>{status}</Badge></div>
              <div className="col-span-10 relative h-10">
                {blocks.map((b,i) => {
                  const ord = orders.find(o=>o.id===b.o)
                  return (
                    <div key={i} className="absolute h-9 rounded bg-slate-800 text-white text-xs p-2 overflow-hidden"
                      style={{ left:`${(b.s/10)*100}%`, width:`${(b.l/10)*100}%` }}>
                      {ord?.id} · {ord?.product}
                    </div>
                  )
                })}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

/* ---------------------------------------------------------
   SCHEDULE PAGE — previous schedule + two alternative reschedules
--------------------------------------------------------- */
function Schedule(){
  const [active, setActive] = useState('original')
  const scenario = scenarios[active]
  const order = ['original','altA','altB']

  return (
    <div>
      <h1 className="text-2xl font-bold">Production Schedule</h1>
      <p className="text-slate-500 mb-5">Constraint-based schedule — previous schedule plus two alternative reschedules after a disruption.</p>

      <div className="flex flex-wrap gap-3 mb-5">
        {order.map(k => (
          <button key={k} onClick={()=>setActive(k)}
            className={`px-4 py-2 rounded-lg text-sm font-medium border ${active===k ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-700'}`}>
            {scenarios[k].label}{scenarios[k].tag ? ` · ${scenarios[k].tag}` : ''}
          </button>
        ))}
      </div>

      <ConstraintsStrip scenario={scenario} />

      <Gantt scenario={scenario} />

      <div className="bg-white border rounded-xl p-4 mt-5 flex gap-3 items-start">
        {active!=='original' && <AlertTriangle size={18} className="text-orange-600 mt-0.5 shrink-0"/>}
        <p className="text-sm text-slate-700">{scenario.note}</p>
      </div>

      <div className="grid md:grid-cols-5 gap-3 mt-5">
        {[['On-Time Delivery',`${scenario.kpis.onTime}%`],['Machine Utilization',`${scenario.kpis.util}%`],['Production Cost',`₹${scenario.kpis.cost.toLocaleString('en-IN')}`],['Downtime',`${scenario.kpis.downtime} min`],['Active Disruptions',scenario.kpis.disruptions]].map(x=>
          <div className="bg-white border rounded-xl p-4" key={x[0]}><p className="text-xs text-slate-500">{x[0]}</p><p className="font-bold text-lg mt-1">{x[1]}</p></div>
        )}
      </div>

      <div className="bg-white border rounded-xl overflow-x-auto mt-5">
        <div className="p-4 border-b font-semibold">Compare All Three</div>
        <table className="w-full text-sm">
          <thead className="bg-slate-50"><tr>
            <th className="text-left p-3">Schedule</th><th className="text-left p-3">On-Time</th><th className="text-left p-3">Utilization</th><th className="text-left p-3">Cost</th><th className="text-left p-3">Downtime</th>
          </tr></thead>
          <tbody className="divide-y">
            {order.map(k => {
              const s = scenarios[k]
              return <tr key={k} className={active===k?'bg-slate-50':''}>
                <td className="p-3 font-medium">{s.label}</td>
                <td className="p-3">{s.kpis.onTime}%</td>
                <td className="p-3">{s.kpis.util}%</td>
                <td className="p-3">₹{s.kpis.cost.toLocaleString('en-IN')}</td>
                <td className="p-3">{s.kpis.downtime} min</td>
              </tr>
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/* ---------------------------------------------------------
   APP
--------------------------------------------------------- */
function App(){
 return <Routes>
   <Route path="/login" element={<Login/>}/>
   <Route path="/" element={<Navigate to="/login" replace/>}/>
   <Route path="/home" element={<Layout><Home/></Layout>}/>
   <Route path="/schedule" element={<Layout><Schedule/></Layout>}/>
   <Route path="/machines" element={<Layout><TablePage title="Machine Status" rows={machines} columns={['id','name','status','order','utilization','operation','remaining']}/></Layout>}/>
   <Route path="/workers" element={<Layout><TablePage title="Worker Status" rows={workers} columns={['id','name','skill','machine','order','status','shift','hours']}/></Layout>}/>
   <Route path="/orders" element={<Layout><TablePage title="Orders" rows={orders} columns={['id','product','qty','priority','deadline','process','setup','machine','status','material']}/></Layout>}/>
   <Route path="/imports" element={<Layout><TablePage title="Import Details" rows={[{id:'IMP-204',material:'Steel Rod',supplier:'ABC Metals',quantity:500,expected:'Today 11:00',actual:'Today 11:20',status:'RECEIVED',affected:'—'},{id:'IMP-205',material:'Control Chips',supplier:'TechSupply',quantity:300,expected:'Today 12:00',actual:'—',status:'DELAYED',affected:'O103'}]} columns={['id','material','supplier','quantity','expected','actual','status','affected']}/></Layout>}/>
   <Route path="/exports" element={<Layout><TablePage title="Export Details" rows={[{id:'EXP-101',order:'O101',product:'Precision Housing',quantity:120,customer:'AutoParts Ltd',destination:'Chennai',planned:'Today 15:00',actual:'—',status:'READY'},{id:'EXP-102',order:'O103',product:'Control Panel',quantity:60,customer:'MechaWorks',destination:'Bengaluru',planned:'Today 14:00',actual:'—',status:'AT RISK'}]} columns={['id','order','product','quantity','customer','destination','planned','actual','status']}/></Layout>}/>
 </Routes>
}
export default App
