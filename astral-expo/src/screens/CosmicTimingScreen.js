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

const TIMING = [
  { dayKey: 'timing.today', vibeKey: 'timing.vibeToday', color: '#80deea' },
  { dayKey: 'timing.tomorrow', vibeKey: 'timing.vibeTomorrow', color: '#ffcc80' },
  { dayKey: 'timing.week', vibeKey: 'timing.vibeWeek', color: '#ff9800' },
  { dayKey: 'timing.month', vibeKey: 'timing.vibeMonth', color: '#ffcc80' },
];

export default function CosmicTimingScreen({ navigation, lang }) {
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
          <Text style={styles.title}>{t(lang, 'timing.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'timing.subtitle')}</Text>
          {TIMING.map((tItem, i) => (
            <TouchableOpacity key={i} style={[styles.card, { borderColor: tItem.color }]} onPress={() => setSelected(tItem.dayKey)}>
              <Text style={[styles.cardTitle, { color: tItem.color }]}>{t(lang, tItem.dayKey)}</Text>
              <Text style={styles.cardText}>{t(lang, tItem.vibeKey)}</Text>
            </TouchableOpacity>
          ))}
          {selected && (
            <View style={styles.detail}>
              <Text style={styles.detailTitle}>{t(lang, selected)} Guidance</Text>
              <Text style={styles.detailText}>{lang === 'th' ? 'ควรทำ: สนทนา วางแผน สร้างสรรค์ หลีกเลี่ยง: รีบร้อนในช่วงจันทร์ว่างเปล่า ช่วงเวลาที่เหมาะสม: 9 โมงเช้า-12 ทุ่ม และ 4 โมงเย็น-7 โมงเย็น' : 'Best actions: communicate, plan, create. Avoid: rushing decisions during void moon periods. Optimal hours: 9am-12pm and 4pm-7pm.'}</Text>
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
  card: { backgroundColor: 'rgba(20,10,40,0.9)', borderWidth: 1.5, borderRadius: 18, padding: 16, marginBottom: 12 },
  cardTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 6 },
  cardText: { color: '#ccddee', fontSize: 13, lineHeight: 20 },
  detail: { backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(255,152,0,0.3)', borderWidth: 1, borderRadius: 18, padding: 16, marginBottom: 20 },
  detailTitle: { color: '#ff9800', fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  detailText: { color: '#ccddee', fontSize: 14, lineHeight: 22 },
  backBtn: { marginTop: 10, alignItems: 'center' },
  backText: { color: '#bb99cc', fontSize: 14 },
});
