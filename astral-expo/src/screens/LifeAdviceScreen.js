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

const CATEGORIES = [
  { id: 'relationship', labelKey: 'advice.relationship', icon: '💕', color: '#ff9800' },
  { id: 'career', labelKey: 'advice.career', icon: '💼', color: '#ffcc80' },
  { id: 'personal', labelKey: 'advice.personal', icon: '🌱', color: '#80deea' },
  { id: 'decisions', labelKey: 'advice.decisions', icon: '⭐', color: '#ffcc80' },
];

const ADVICE = {
  relationship: 'Venus transiting your 7th house favors partnerships. Communication flow improves mid-month. Existing bonds deepen through shared vulnerability. Singles: social settings after the 12th hold potential.',
  career: 'Jupiter in 10th expands opportunities. Saturn rewards consistency. Best launch window: after Mercury direct on the 18th.',
  personal: 'Full moon in your sign brings emotional release. Neptune supports spiritual practices. Journaling and meditation recommended daily.',
  decisions: 'Mercury sextile Jupiter favors sign-and-commit decisions. Moon void-of-course periods to avoid action: 3rd, 9th, 17th, 24th.',
};

export default function LifeAdviceScreen({ navigation, lang }) {
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
          <Text style={styles.title}>{t(lang, 'advice.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'advice.subtitle')}</Text>
          <View style={styles.grid}>
            {CATEGORIES.map(cat => (
              <TouchableOpacity key={cat.id} style={[styles.card, { borderColor: cat.color }]} onPress={() => setSelected(cat.id)}>
                <Text style={styles.icon}>{cat.icon}</Text>
                <Text style={[styles.cardLabel, { color: cat.color }]}>{t(lang, cat.labelKey)}</Text>
              </TouchableOpacity>
            ))}
          </View>
          {selected ? (
            <View style={styles.result}>
              <Text style={styles.resultTitle}>{t(lang, CATEGORIES.find(c => c.id === selected)?.labelKey)}</Text>
              <Text style={styles.resultText}>{ADVICE[selected]}</Text>
            </View>
          ) : null}
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
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, marginBottom: 20 },
  card: { width: '46%', backgroundColor: 'rgba(20,10,40,0.9)', borderWidth: 1.5, borderRadius: 18, padding: 20, alignItems: 'center', marginBottom: 12, shadowColor: '#ff9800', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 12, elevation: 8 },
  icon: { fontSize: 36, marginBottom: 10 },
  cardLabel: { fontSize: 14, fontWeight: 'bold' },
  result: { backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(255,152,0,0.3)', borderWidth: 1, borderRadius: 18, padding: 16, marginBottom: 20 },
  resultTitle: { color: '#ff9800', fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  resultText: { color: '#ccddee', fontSize: 14, lineHeight: 22 },
  backBtn: { marginTop: 10, alignItems: 'center' },
  backText: { color: '#bb99cc', fontSize: 14 },
});
