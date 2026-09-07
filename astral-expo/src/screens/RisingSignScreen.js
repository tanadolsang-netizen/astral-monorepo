import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated } from 'react-native';
import Starfield from '../components/Starfield';
import { translations } from '../i18n';

const t = (lang, key) => {
  const parts = key.split('.');
  let cur = translations[lang] || translations.en;
  for (const p of parts) cur = cur?.[p];
  return cur || key;
};

const SIGNS = [
  { name: 'Aries', emoji: '♈', color: '#ff6b6b', trait: 'Bold, pioneering, confident' },
  { name: 'Taurus', emoji: '♉', color: '#feca57', trait: 'Steady, sensual, reliable' },
  { name: 'Gemini', emoji: '♊', color: '#ff9f43', trait: 'Curious, adaptable, witty' },
  { name: 'Cancer', emoji: '♋', color: '#a29bfe', trait: 'Nurturing, intuitive, protective' },
  { name: 'Leo', emoji: '♌', color: '#ff6b9d', trait: 'Charismatic, creative, warm' },
  { name: 'Virgo', emoji: '♍', color: '#54a0ff', trait: 'Analytical, precise, helpful' },
  { name: 'Libra', emoji: '♎', color: '#f368e0', trait: 'Diplomatic, charming, balanced' },
  { name: 'Scorpio', emoji: '♏', color: '#c44569', trait: 'Intense, transformative, deep' },
  { name: 'Sagittarius', emoji: '♐', color: '#78e08f', trait: 'Adventurous, optimistic, wise' },
  { name: 'Capricorn', emoji: '♑', color: '#82ccdd', trait: 'Ambitious, disciplined, patient' },
  { name: 'Aquarius', emoji: '♒', color: '#60a3bc', trait: 'Innovative, independent, humanitarian' },
  { name: 'Pisces', emoji: '♓', color: '#7ed6df', trait: 'Compassionate, artistic, dreamy' },
];

export default function RisingSignScreen({ navigation, lang }) {
  const [selected, setSelected] = useState(null);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>{t(lang, 'rising.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'rising.subtitle')}</Text>
          <View style={styles.grid}>
            {SIGNS.map(sign => (
              <TouchableOpacity key={sign.name} style={[styles.signCard, { borderColor: sign.color }]} onPress={() => setSelected(sign.name)}>
                <Text style={styles.signEmoji}>{sign.emoji}</Text>
                <Text style={[styles.signName, { color: sign.color }]}>{sign.name}</Text>
                <Text style={styles.signTrait}>{sign.trait}</Text>
              </TouchableOpacity>
            ))}
          </View>
          {selected && (
            <View style={styles.detail}>
              <Text style={styles.detailTitle}>{selected}</Text>
              <Text style={styles.detailText}>{lang === 'th' ? `ลักษณะภายนอก: ${SIGNS.find(s => s.name === selected)?.trait}` : `First impression: ${SIGNS.find(s => s.name === selected)?.trait}`}</Text>
              <Text style={styles.detailText}>{lang === 'th' ? `คนอื่นมองคุณว่า ${SIGNS.find(s => s.name === selected)?.trait.toLowerCase()}` : `Others see you as ${SIGNS.find(s => s.name === selected)?.trait.toLowerCase()}`}</Text>
            </View>
          )}
          <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
            <Text style={styles.backText}>{t(lang, 'back')}</Text>
          </TouchableOpacity>
        </ScrollView>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a0b2e' },
  scroll: { padding: 20, paddingTop: 60 },
  title: { fontSize: 32, color: '#fff', fontWeight: 'bold', textAlign: 'center', marginBottom: 8, textShadowColor: '#ff9800', textShadowRadius: 20 },
  subtitle: { fontSize: 14, color: '#bb99cc', textAlign: 'center', marginBottom: 30 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20 },
  signCard: { width: '30%', backgroundColor: 'rgba(20,10,40,0.9)', borderWidth: 1.5, borderRadius: 14, padding: 12, alignItems: 'center', marginBottom: 10 },
  signEmoji: { fontSize: 28, marginBottom: 6 },
  signName: { fontSize: 13, fontWeight: 'bold', marginBottom: 4 },
  signTrait: { fontSize: 10, color: '#bb99cc', textAlign: 'center' },
  detail: { backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(255,152,0,0.3)', borderWidth: 1, borderRadius: 18, padding: 16, marginBottom: 20 },
  detailTitle: { color: '#ff9800', fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  detailText: { color: '#ccddee', fontSize: 14, lineHeight: 22, marginBottom: 8 },
  backBtn: { marginTop: 10, alignItems: 'center' },
  backText: { color: '#bb99cc', fontSize: 14 },
});
