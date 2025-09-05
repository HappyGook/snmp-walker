import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '../public/vite.svg'
import './App.css'

function App() {
  const [ip, setIp] = useState("")
  const [metrics, setMetrics]=useState()


  async function handleWalk() {
      console.log('Sending walk request');
      await fetch('/api/walk', {
          method: 'POST',
          headers: {
              "Content-type": "application/json"
          },
          body: JSON.stringify({ip})
      }).then(res=>res.json()).then(data=>setMetrics(data));
      console.log(JSON.stringify(metrics))


  }

  function handleIP(e) {
      e.preventDefault();
      setIp(e.target.value);
  }

  return (
      <>
          <div>
              <a href="https://vite.dev" target="_blank">
                  <img src={viteLogo} className="logo" alt="Vite logo"/>
              </a>
              <a href="https://react.dev" target="_blank">
                  <img src={reactLogo} className="logo react" alt="React logo"/>
              </a>
          </div>
          <h1>Vite + React</h1>
          <label htmlFor="input-ip">Ziel für den Walk eingeben:</label>
          <input type="text" id="input-ip" onChange={handleIP}/>
          <div className="card">
              <button onClick={handleWalk}>
                  SNMP WALK
              </button>
          </div>
          Das wird später im Datei abgelegt
          {metrics && metrics.status === "success" && (
          <table>
            <thead>
              <tr>
                <th>OID</th>
                <th>Value</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {metrics.data.map((item, idx) => (
                <tr key={idx}>
                  <td>{item.oid}</td>
                  <td>{item.value}</td>
                  <td>{item.type}</td>
                </tr>
              ))}
            </tbody>
          </table>
            )}
      </>
  )
}

export default App
