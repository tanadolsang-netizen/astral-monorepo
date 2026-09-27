import { Component } from 'react'

/* Error boundary รอบเฉพาะ <Canvas> WebGL — ถ้า context lost/panic
   จะกิน error ตรงนี้ ไม่ให้ลามทำลาย UI (ฟอร์ม/ปุ่ม API ยังใช้งานได้) */
export default class CanvasBoundary extends Component {
  constructor(p){ super(p); this.state={ failed:false } }
  static getDerivedStateFromError(){ return { failed:true } }
  componentDidCatch(err){ console.warn('CanvasBoundary caught:', err?.message || err) }
  render(){
    if (this.state.failed) return this.props.fallback || null
    return this.props.children
  }
}
