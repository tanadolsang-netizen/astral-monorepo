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

export default function TransitScreen({ navigation, lang }) {
  const [natalDate, setNatalDate] = useState('');
  const [transitDate, setTransitDate] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }).start();
  }, []);

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ flex: 1, opacity: fadeAnim }}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text style={styles.title}>{t(lang, 'transit.title')}</Text>
          <Text style={styles.subtitle}>{t(lang, 'transit.subtitle')}</Text>
          <TextInput style={styles.input} placeholder={t(lang, 'transit.natalDate')} placeholderTextColor="#bb99cc" value={natalDate} onChangeText={setNatalDate} />
          <TextInput style={styles.input} placeholder={t(lang, 'transit.transitDate')} placeholderTextColor="#bb99cc" value={transitDate} onChangeText={setTransitDate} />
          <TouchableOpacity style={styles.btn} onPress={() => Alert.alert('Transit', `${natalDate} → ${transitDate}`)}>
            <Text style={styles.btnText}>{t(lang, 'transit.calculate')}</Text>
          </TouchableOpacity>
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
  input: { backgroundColor: 'rgba(20,10,40,0.8)', borderColor: 'rgba(128,222,234,0.4)', borderWidth: 1, borderRadius: 16, padding: 14, color: '#fff', marginBottom: 12, fontSize: 14 },
  btn: { backgroundColor: '#80deea', padding: 16, borderRadius: 999, alignItems: 'center', marginTop: 10, shadowColor: '#80deea', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.5, shadowRadius: 20, elevation: 12 },
  btnText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 16 },
  backBtn: { marginTop: 20, alignItems: 'center' },
  backText: { color: '#bb99cc', fontSize: 14 },
});
