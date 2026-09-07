import { useState, useCallback } from 'react'

const API = 'http://127.0.0.1:8000'

export function useAstralApi(){
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const call = useCallback(async (kind, box, payload) => {
    setLoading(true); setError(null)
    box.classList.add('show'); box.innerHTML = '⏳ กำลังอ่านดาวให้ท่านฟัง...'
    try {
      const res = await fetch(API + payload.url, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload.body)
      })
      const data = await res.json()
      if (data.file) {
        box.innerHTML = `✅ ดาวบอกท่านครบแล้ว (${data.sections} หน้า)<br><a href="${API}/v1/reports/pdf/download?file=${encodeURIComponent(data.file)}" target="_blank">อ่านรายงานที่ฟ้าฝากมา</a>`
      } else if (data.cards) {
        window.__renderTarot(box, data)
      } else {
        box.innerHTML = '✅ ' + JSON.stringify(data).slice(0, 300)
      }
    } catch (e) {
      box.innerHTML = '❌ ' + e
      setError(e)
    } finally { setLoading(false) }
  }, [])

  return { call, loading, error }
}
