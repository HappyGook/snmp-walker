import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '../public/vite.svg'
import './App.css'

function App() {
  const [ip, setIp] = useState("")


  async function handleWalk() {
      console.log('Sending walk request');
      const response = await fetch('/api/walk', {
          method: 'POST',
          body: JSON.stringify({ip}),
          headers: {
              'Accept': 'application/json'
          }
      });

      console.log('Response status:', response.status);
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
      </>
  )
}

export default App
