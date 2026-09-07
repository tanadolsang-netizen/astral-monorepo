import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Dimensions, ScrollView, Animated } from 'react-native';
import Starfield from '../components/Starfield';
import ZodiacWheel3D from '../components/ZodiacWheel3D';
import { translations } from '../i18n';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const SECTIONS = [
  { id: 'natal', labelKey: 'natal', icon: '🌟', color: '#ff9800', descKey: 'natal', screen: 'natal' },
  { id: 'transit', labelKey: 'transit', icon: '🔄', color: '#80deea', descKey: 'transit', screen: 'transit' },
  { id: 'synastry', labelKey: 'synastry', icon: '💕', color: '#ff6b9d', descKey: 'synastry', screen: 'synastry' },
  { id: 'tarot', labelKey: 'tarot', icon: '🃏', color: '#a29bfe', descKey: 'tarot', screen: 'tarot' },
  { id: 'thai', labelKey: 'thai', icon: '🙏', color: '#feca57', descKey: 'thai', screen: 'thai' },
];

const FEATURES = [
  { id: 'chat', labelKey: 'chat', icon: '💬', color: '#80deea', descKey: 'chat', screen: 'chat' },
  { id: 'chart', labelKey: 'chart', icon: '📖', color: '#80deea', descKey: 'chart', screen: 'chart' },
  { id: 'advice', labelKey: 'advice', icon: '💡', color: '#ff9800', descKey: 'advice', screen: 'advice' },
  { id: 'rising', labelKey: 'rising', icon: '🌙', color: '#a29bfe', descKey: 'rising', screen: 'rising' },
  { id: 'timing', labelKey: 'timing', icon: '⏳', color: '#78e08f', descKey: 'timing', screen: 'timing' },
  { id: 'about', labelKey: 'about', icon: 'ℹ️', color: '#aabbcc', descKey: 'about', screen: 'about' },
];

const t = (lang, key) => {
  const parts = key.split('.');
  let cur = translations[lang] || translations.en;
  for (const p of parts) {
    cur = cur?.[p];
  }
  return cur || key;
};

const SectionCard = ({ item, index, lang, navigation }) => {
  const anim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(400 + index * 80),
      Animated.parallel([
        Animated.spring(anim, { toValue: 1, friction: 4, tension: 35, useNativeDriver: true }),
        Animated.timing(anim, { toValue: 1, duration: 600, useNativeDriver: true }),
      ]),
    ]).start();
  }, []);

  const translateY = anim.interpolate({ inputRange: [0, 1], outputRange: [30, 0] });
  const opacity = anim;

  return (
    <Animated.View style={{ opacity, transform: [{ translateY }] }}>
      <TouchableOpacity style={styles.card} onPress={() => navigation.navigate(item.screen)} activeOpacity={0.85}>
        <View style={[styles.iconWrap, { backgroundColor: item.color + '22' }]}>
          <Text style={styles.cardIcon}>{item.icon}</Text>
        </View>
        <View style={styles.cardText}>
          <Text style={[styles.cardTitle, { color: item.color }]}>{t(lang, item.labelKey)}</Text>
          <Text style={styles.cardDesc}>{t(lang, item.descKey)}</Text>
        </View>
        <Text style={styles.arrow}>›</Text>
      </TouchableOpacity>
    </Animated.View>
  );
};

export default function HomeScreen({ navigation, lang }) {
  const headerAnim = useRef(new Animated.Value(0)).current;
  const wheelAnim = useRef(new Animated.Value(0)).current;
  const home = translations[lang]?.home || translations.en.home;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(200),
      Animated.parallel([
        Animated.spring(headerAnim, { toValue: 1, friction: 4, tension: 30, useNativeDriver: true }),
        Animated.spring(wheelAnim, { toValue: 1, friction: 3, tension: 30, useNativeDriver: true }),
      ]),
    ]).start();
  }, []);

  return (
    <View style={styles.container}>
      <Starfield />
      <Animated.View style={{ position: 'absolute', top: 0, left: 0, right: 0, opacity: wheelAnim, transform: [{ scale: wheelAnim }] }}>
        <ZodiacWheel3D />
      </Animated.View>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Animated.View style={{ opacity: headerAnim, transform: [{ translateY: headerAnim.interpolate({ inputRange: [0, 1], outputRange: [-20, 0] }) }] }}>
          <Text style={styles.heroTitle}>{home.title}</Text>
          <Text style={styles.heroAccent}>{home.accent}</Text>
          <Text style={styles.heroSub}>{home.subtitle}</Text>
          <TouchableOpacity style={styles.cta} onPress={() => navigation.navigate('natal')}>
            <Text style={styles.ctaText}>{home.cta}</Text>
          </TouchableOpacity>
        </Animated.View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{home.discover}</Text>
          {SECTIONS.map((item, index) => (
            <SectionCard key={item.id} item={item} index={index} lang={lang} navigation={navigation} />
          ))}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>{home.featured}</Text>
          {FEATURES.map((item, index) => (
            <SectionCard key={item.id} item={item} index={index + SECTIONS.length} lang={lang} navigation={navigation} />
          ))}
        </View>

        <View style={styles.bottomSpacer} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a0b2e' },
  scroll: { padding: 20, paddingTop: 70, paddingBottom: 100 },
  heroTitle: { fontSize: 36, color: '#fff', fontWeight: 'bold', textAlign: 'center', letterSpacing: 1 },
  heroAccent: { fontSize: 52, color: '#ff9800', fontWeight: 'bold', textAlign: 'center', marginBottom: 8, textShadowColor: '#ff6f00', textShadowRadius: 30, letterSpacing: 2 },
  heroSub: { fontSize: 12, color: '#bb99cc', textAlign: 'center', marginBottom: 30, letterSpacing: 1.5 },
  cta: { backgroundColor: '#ff9800', paddingVertical: 16, paddingHorizontal: 50, borderRadius: 999, alignSelf: 'center', shadowColor: '#ff9800', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.6, shadowRadius: 20, elevation: 12, marginBottom: 50 },
  ctaText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 16, letterSpacing: 1 },
  section: { marginTop: 10, marginBottom: 30 },
  sectionTitle: { fontSize: 22, color: '#ffcc80', fontWeight: 'bold', marginBottom: 16, letterSpacing: 1 },
  card: { flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(20,10,40,0.7)', borderColor: 'rgba(255,152,0,0.2)', borderWidth: 1, borderRadius: 18, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOffset: { width: 0, height: 3 }, shadowOpacity: 0.3, shadowRadius: 8, elevation: 6 },
  iconWrap: { width: 48, height: 48, borderRadius: 14, alignItems: 'center', justifyContent: 'center', marginRight: 14 },
  cardIcon: { fontSize: 24 },
  cardText: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: '700', marginBottom: 3, letterSpacing: 0.5 },
  cardDesc: { fontSize: 12, color: '#bb99cc', lineHeight: 16 },
  arrow: { fontSize: 28, color: '#ff9800', fontWeight: '300', marginLeft: 10 },
  bottomSpacer: { height: 40 },
});
