import React, { useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import HomeScreen from './src/screens/HomeScreen';
import NatalScreen from './src/screens/NatalScreen';
import TransitScreen from './src/screens/TransitScreen';
import SynastryScreen from './src/screens/SynastryScreen';
import TarotScreen from './src/screens/TarotScreen';
import ThaiScreen from './src/screens/ThaiScreen';
import ChatScreen from './src/screens/ChatScreen';
import ChartInterpretationScreen from './src/screens/ChartInterpretationScreen';
import LifeAdviceScreen from './src/screens/LifeAdviceScreen';
import RisingSignScreen from './src/screens/RisingSignScreen';
import CosmicTimingScreen from './src/screens/CosmicTimingScreen';
import AboutScreen from './src/screens/AboutScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  const [lang, setLang] = useState('en');

  const toggleLang = () => setLang(prev => prev === 'en' ? 'th' : 'en');

  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#1a0b2e' },
        }}
      >
        <Stack.Screen name="Home">
          {props => <HomeScreen {...props} lang={lang} toggleLang={toggleLang} />}
        </Stack.Screen>
        <Stack.Screen name="natal">
          {props => <NatalScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="transit">
          {props => <TransitScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="synastry">
          {props => <SynastryScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="tarot">
          {props => <TarotScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="thai">
          {props => <ThaiScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="chat">
          {props => <ChatScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="chart">
          {props => <ChartInterpretationScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="advice">
          {props => <LifeAdviceScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="rising">
          {props => <RisingSignScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="timing">
          {props => <CosmicTimingScreen {...props} lang={lang} />}
        </Stack.Screen>
        <Stack.Screen name="about">
          {props => <AboutScreen {...props} lang={lang} />}
        </Stack.Screen>
      </Stack.Navigator>

      {/* Floating language toggle */}
      <TouchableOpacity style={styles.langBtn} onPress={toggleLang}>
        <Text style={styles.langText}>{lang === 'en' ? '🇹🇭 TH' : '🇬🇧 EN'}</Text>
      </TouchableOpacity>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  langBtn: {
    position: 'absolute',
    top: 50,
    right: 20,
    backgroundColor: 'rgba(255,152,0,0.9)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 999,
    shadowColor: '#ff9800',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.6,
    shadowRadius: 8,
    elevation: 6,
    zIndex: 999,
  },
  langText: { color: '#1a0b2e', fontWeight: 'bold', fontSize: 13, letterSpacing: 1 },
});
