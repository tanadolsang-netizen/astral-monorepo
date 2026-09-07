import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Dimensions, Text } from 'react-native';
import Svg, { Circle, Text as SvgText, G, Path, Defs, RadialGradient, Stop } from 'react-native-svg';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const SIZE = Math.min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.7;
const CENTER = SIZE / 2;
const RADIUS = SIZE / 2 - 20;

const SIGNS = [
  { name: 'Aries', emoji: '♈', color: '#ff6b6b', angle: 0 },
  { name: 'Taurus', emoji: '♉', color: '#feca57', angle: 30 },
  { name: 'Gemini', emoji: '♊', color: '#ff9f43', angle: 60 },
  { name: 'Cancer', emoji: '♋', color: '#a29bfe', angle: 90 },
  { name: 'Leo', emoji: '♌', color: '#ff6b9d', angle: 120 },
  { name: 'Virgo', emoji: '♍', color: '#54a0ff', angle: 150 },
  { name: 'Libra', emoji: '♎', color: '#f368e0', angle: 180 },
  { name: 'Scorpio', emoji: '♏', color: '#c44569', angle: 210 },
  { name: 'Sagittarius', emoji: '♐', color: '#78e08f', angle: 240 },
  { name: 'Capricorn', emoji: '♑', color: '#82ccdd', angle: 270 },
  { name: 'Aquarius', emoji: '♒', color: '#60a3bc', angle: 300 },
  { name: 'Pisces', emoji: '♓', color: '#7ed6df', angle: 330 },
];

export default function ZodiacWheel3D() {
  const rotateAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.3)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(300),
      Animated.parallel([
        Animated.spring(scaleAnim, { toValue: 1, friction: 4, tension: 40, useNativeDriver: true }),
        Animated.timing(opacityAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
      ]),
    ]).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(rotateAnim, { toValue: 1, duration: 40000, useNativeDriver: true }),
        Animated.timing(rotateAnim, { toValue: 0, duration: 0, useNativeDriver: true }),
      ])
    ).start();

    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.05, duration: 2000, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1, duration: 2000, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  const rotation = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const renderSigns = () => {
    return SIGNS.map((sign, index) => {
      const angleRad = (sign.angle * Math.PI) / 180;
      const x = CENTER + RADIUS * 0.75 * Math.cos(angleRad);
      const y = CENTER + RADIUS * 0.75 * Math.sin(angleRad);
      const opacity = opacityAnim.interpolate({
        inputRange: [0, 0.5, 1],
        outputRange: [0, index % 2 === 0 ? 1 : 0.6, 1],
      });
      return (
        <G key={sign.name}>
          <SvgText
            x={x}
            y={y}
            fontSize={24}
            fill={sign.color}
            textAnchor="middle"
            alignmentBaseline="middle"
            opacity={opacity}
          >
            {sign.emoji}
          </SvgText>
          <SvgText
            x={x}
            y={y + 22}
            fontSize={10}
            fill="#8899aa"
            textAnchor="middle"
            opacity={opacity}
          >
            {sign.name}
          </SvgText>
        </G>
      );
    });
  };

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.wheelContainer,
          {
            transform: [{ rotate: rotation }, { scale: Animated.multiply(scaleAnim, pulseAnim) }],
            opacity: opacityAnim,
          },
        ]}
      >
        <Svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
          <Defs>
            <RadialGradient id="grad" cx="50%" cy="50%" r="50%">
              <Stop offset="0%" stopColor="#1a1a3e" stopOpacity="0.8" />
              <Stop offset="70%" stopColor="#0a0a1f" stopOpacity="0.4" />
              <Stop offset="100%" stopColor="#05050f" stopOpacity="0" />
            </RadialGradient>
          </Defs>
          <Circle cx={CENTER} cy={CENTER} r={RADIUS} fill="url(#grad)" stroke="#334455" strokeWidth="1.5" opacity={0.6} />
          {SIGNS.map((sign, index) => {
            const angleRad = (sign.angle * Math.PI) / 180;
            const nextAngleRad = ((sign.angle + 30) * Math.PI) / 180;
            const x1 = CENTER + (RADIUS - 15) * Math.cos(angleRad);
            const y1 = CENTER + (RADIUS - 15) * Math.sin(angleRad);
            const x2 = CENTER + (RADIUS - 15) * Math.cos(nextAngleRad);
            const y2 = CENTER + (RADIUS - 15) * Math.sin(nextAngleRad);
            return (
              <Path
                key={`line-${index}`}
                d={`M ${CENTER} ${CENTER} L ${x1} ${y1} L ${x2} ${y2} Z`}
                stroke={sign.color}
                strokeWidth="0.5"
                fill="none"
                opacity={0.3}
              />
            );
          })}
          <Circle cx={CENTER} cy={CENTER} r={RADIUS} fill="none" stroke="#ff9f43" strokeWidth="2" opacity={0.4} />
          <Circle cx={CENTER} cy={CENTER} r={RADIUS * 0.2} fill="#ff9f43" opacity={0.2} />
          <Circle cx={CENTER} cy={CENTER} r={6} fill="#fff" opacity={0.9} />
        </Svg>
        {renderSigns()}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
    pointerEvents: 'none',
  },
  wheelContainer: {
    width: SIZE,
    height: SIZE,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
