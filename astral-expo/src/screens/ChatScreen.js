import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, Animated } from 'react-native';
import Starfield from '../components/Starfield';
import { translations } from '../i18n';

const t = (lang, key) => {
  const parts = key.split('.');
  let cur = translations[lang] || translations.en;
  for (const p of parts) cur = cur?.[p];
  return cur || key;
};

export default function ChatScreen({ navigation, lang }) {
  const [messages, setMessages] = useState([
    { id: 1, role: 'bot', text: lang === 'th' ? 'ยินดีต้อนรับสู่ Astra ถามอะไรก็ได้เกี่ยวกับความรัก การงาน เงิน หรือชีวิต' : 'Welcome to Astra Ask Me Anything. Ask about love, career, money, or life decisions.' },
  ]);
  const [input, setInput] = useState('');
  const scrollRef = useRef(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    const userMsg = { id: Date.now(), role: 'user', text };
    const lower = text.toLowerCase();
    let reply = lang === 'th' ? 'ตาม birth chart ปัจจุบัน แนะนำให้ contemplat การตัดสินใจ carefully' : 'Based on your chart, the current transit emphasizes self-reflection.';
        if (lower.includes('love') || lower.includes('relationship') || lower.includes('รัก')) reply = lang === 'th' ? 'Venus อยู่ตำแหน่งดี สัปดาห์นี้มี prospects ช่วงกลางเดือนเป็นช่วงดีกว่าสำหรับคนโสด' : 'Venus placement shows strong attraction energy this week.';
        else if (lower.includes('career') || lower.includes('งาน') || lower.includes('job')) reply = lang === 'th' ? 'Jupiter ใน 10th house โปร่ง related to career จะเริ่มชัดเจนหลังวันที่ 15' : 'Jupiter in your 10th house signals expansion.';
    else if (lower.includes('money') || lower.includes('เงิน') || lower.includes('finance')) reply = lang === 'th' ? 'ระวัง impulsive buys ระ Hernández full moon เป็นช่วงดีสำหรับการตรวจสอบการลงทุน' : 'Mars-Neptune aspect warns against impulsive buys.';
    const botMsg = { id: Date.now() + 1, role: 'bot', text: reply };
    setMessages(prev => [...prev, userMsg, botMsg]);
    setInput('');
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
  };

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView ref={scrollRef} contentContainerStyle={styles.scroll} onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}>
          {messages.map(m => (
            <View key={m.id} style={[styles.msg, m.role === 'user' ? styles.user : styles.bot]}>
              <Text style={[styles.msgText, m.role === 'user' ? styles.userText : styles.botText]}>{m.text}</Text>
            </View>
          ))}
        </ScrollView>
        <View style={styles.inputRow}>
          <TextInput style={styles.input} placeholder={t(lang, 'chat.placeholder')} placeholderTextColor="#bb99cc" value={input} onChangeText={setInput} onSubmitEditing={send} />
          <TouchableOpacity style={styles.sendBtn} onPress={send}><Text style={styles.sendText}>➤</Text></TouchableOpacity>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a0b2e' },
  scroll: { padding: 16, paddingTop: 60, paddingBottom: 20 },
  msg: { maxWidth: '80%', padding: 14, borderRadius: 18, marginBottom: 12 },
  user: { alignSelf: 'flex-end', backgroundColor: '#ff9800' },
  bot: { alignSelf: 'flex-start', backgroundColor: 'rgba(30,15,50,0.95)', borderColor: 'rgba(255,152,0,0.3)', borderWidth: 1 },
  msgText: { fontSize: 14, lineHeight: 20 },
  userText: { color: '#1a0b2e', fontWeight: '600' },
  botText: { color: '#e0e0e0' },
  inputRow: { flexDirection: 'row', padding: 12, borderTopColor: 'rgba(255,152,0,0.15)', borderTopWidth: 1, gap: 8 },
  input: { flex: 1, backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(255,152,0,0.3)', borderWidth: 1, borderRadius: 999, padding: 12, color: '#fff', fontSize: 14 },
  sendBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#ff9800', alignItems: 'center', justifyContent: 'center', shadowColor: '#ff9800', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.6, shadowRadius: 8, elevation: 6 },
  sendText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 16 },
});
