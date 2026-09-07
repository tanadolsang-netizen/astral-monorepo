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

export default function ChartInterpretationScreen({ navigation, lang }) {
  const [reading, setReading] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>{t(lang, 'chart.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'chart.subtitle')}</Text>
          <TouchableOpacity style={styles.btn} onPress={() => setReading(lang === 'th' ? 'Sun ใน Leo: ความเป็นผู้นำ การสร้างสรรค์ และความอบอุ่นเป็นตัวตนเอง Moon ใน Pisces: การทำความเข้าใจอารมณ์และรู้สึกอย่างลึกซึ้ง' : 'Sun in Leo: Leadership, creativity, warmth. Moon in Pisces: Intuition and empathy. Mercury in Virgo: Analytical precision. Venus in Libra: Harmony in relationships. Mars in Aries: Pioneering energy. Jupiter in Sagittarius: Expansion through adventure.')}>
            <Text style={styles.btnText}>{t(lang, 'chart.generate')}</Text>
          </TouchableOpacity>
          {reading ? (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>{t(lang, 'chart.blueprint')}</Text>
              <Text style={styles.cardText}>{reading}</Text>
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
  title: { fontSize: 32, color: '#fff', fontWeight: 'bold', textAlign: 'center', marginBottom: 8, textShadowColor: '#80deea', textShadowRadius: 20 },
  subtitle: { fontSize: 14, color: '#bb99cc', textAlign: 'center', marginBottom: 30 },
  btn: { backgroundColor: '#80deea', padding: 16, borderRadius: 999, alignItems: 'center', marginBottom: 20, shadowColor: '#80deea', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.5, shadowRadius: 20, elevation: 12 },
  btnText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 16 },
  card: { backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(128,222,234,0.3)', borderWidth: 1, borderRadius: 18, padding: 16, marginBottom: 20 },
  cardTitle: { color: '#80deea', fontSize: 18, fontWeight: 'bold', marginBottom: 12 },
  cardText: { color: '#ccddee', fontSize: 14, lineHeight: 22 },
  backBtn: { marginTop: 10, alignItems: 'center' },
  backText: { color: '#bb99cc', fontSize: 14 },
});
