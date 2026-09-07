import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated } from 'react-native';
import Starfield from '../components/Starfield';
import { translations } from '../i18n';

const t = (lang, key) => {
  const parts = key.split('.');
  let cur = translations[lang] || translations.en;
  for (const p of parts) cur = cur?.[p];
  return cur || key;
};

export default function AboutScreen({ navigation, lang }) {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>{t(lang, 'about.title')}</Text>
          <Text style={styles.version}>{t(lang, 'about.version')}</Text>
          <Text style={styles.desc}>{t(lang, 'about.desc')}</Text>
          <Text style={styles.features}>{t(lang, 'about.features')}</Text>
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
  title: { fontSize: 48, color: '#ff9800', fontWeight: 'bold', marginBottom: 10, textShadowColor: '#ff6f00', textShadowRadius: 30 },
  version: { fontSize: 14, color: '#bb99cc', marginBottom: 20 },
  desc: { fontSize: 16, color: '#fff', marginBottom: 20, textAlign: 'center' },
  features: { fontSize: 13, color: '#bb99cc', textAlign: 'center', lineHeight: 20, marginBottom: 40 },
  backBtn: { marginTop: 20 },
  backText: { color: '#bb99cc', fontSize: 14 },
});
