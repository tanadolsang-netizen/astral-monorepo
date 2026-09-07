import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, Animated } from 'react-native';
import Starfield from '../components/Starfield';
import { translations } from '../i18n';
import { drawTarot } from '../tarotNamesTh';

const t = (lang, key) => {
  const parts = key.split('.');
  let cur = translations[lang] || translations.en;
  for (const p of parts) cur = cur?.[p];
  return cur || key;
};

export default function TarotScreen({ navigation, lang }) {
  const [drawn, setDrawn] = useState([]);
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  const draw = () => {
    // Draw 3 cards from the full 78-card deck; display poetic Thai names.
    setDrawn(drawTarot(3));
  };

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>{t(lang, 'tarot.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'tarot.subtitle')}</Text>
          <TouchableOpacity style={styles.btn} onPress={draw}>
            <Text style={styles.btnText}>{t(lang, 'tarot.draw')}</Text>
          </TouchableOpacity>
          <View style={styles.cards}>
            {drawn.map((card, i) => (
              <View key={i} style={styles.card}>
                <Text style={styles.cardIcon}>🃏</Text>
                <Text style={styles.cardText}>
                  {lang === 'th' ? card.th : card.en}
                </Text>
                <Text style={styles.cardOrient}>
                  {card.reversed
                    ? (lang === 'th' ? 'หงายหลัง' : 'Reversed')
                    : (lang === 'th' ? 'ตั้งตรง' : 'Upright')}
                </Text>
              </View>
            ))}
          </View>
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
  scroll: { padding: 20, paddingTop: 60, alignItems: 'center' },
  title: { fontSize: 32, color: '#fff', fontWeight: 'bold', marginBottom: 30, textShadowColor: '#ff9800', textShadowRadius: 20 },
  subtitle: { fontSize: 14, color: '#bb99cc', textAlign: 'center', marginBottom: 30 },
  btn: { backgroundColor: '#ff9800', padding: 16, borderRadius: 999, alignItems: 'center', paddingHorizontal: 50, marginBottom: 30, shadowColor: '#ff9800', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.5, shadowRadius: 20, elevation: 12 },
  btnText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 16 },
  cards: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 12 },
  card: { width: 90, aspectRatio: 0.65, backgroundColor: 'rgba(20,10,40,0.9)', borderColor: 'rgba(255,152,0,0.4)', borderWidth: 1.5, borderRadius: 16, alignItems: 'center', justifyContent: 'center', padding: 8, shadowColor: '#ff9800', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.3, shadowRadius: 10, elevation: 8 },
  cardIcon: { fontSize: 32, marginBottom: 8 },
  cardText: { color: '#fff', fontSize: 10, textAlign: 'center' },
  cardOrient: { color: '#ffb74d', fontSize: 9, textAlign: 'center', marginTop: 4 },
  backBtn: { marginTop: 40 },
  backText: { color: '#bb99cc', fontSize: 14 },
});
