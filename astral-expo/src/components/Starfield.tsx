import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated, Dimensions, Platform } from 'react-native';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface Star {
  x: number;
  y: number;
  size: number;
  speed: number;
  opacity: number;
  twinkleSpeed: number;
  depth: number;
}

const generateStars = (count: number): Star[] => {
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    stars.push({
      x: Math.random() * SCREEN_WIDTH,
      y: Math.random() * SCREEN_HEIGHT,
      size: Math.random() * 2.5 + 0.5,
      speed: Math.random() * 0.4 + 0.1,
      opacity: Math.random() * 0.8 + 0.2,
      twinkleSpeed: Math.random() * 2000 + 1000,
      depth: Math.random() * 0.5 + 0.5,
    });
  }
  return stars;
};

export default function Starfield() {
  const starsRef = useRef<Star[]>(generateStars(120));
  const animValues = useRef(
    starsRef.current.map(() => ({
      y: new Animated.Value(Math.random() * SCREEN_HEIGHT),
      opacity: new Animated.Value(Math.random() * 0.8 + 0.2),
    }))
  ).current;

  useEffect(() => {
    const animations = starsRef.current.map((star, index) => {
      const anim = animValues[index];
      const duration = (SCREEN_HEIGHT / star.speed) * 15;
      return Animated.loop(
        Animated.sequence([
          Animated.timing(anim.y, {
            toValue: -20,
            duration: duration,
            useNativeDriver: true,
          }),
          Animated.timing(anim.y, {
            toValue: SCREEN_HEIGHT + 20,
            duration: 0,
            useNativeDriver: true,
          }),
        ])
      );
    });

    const twinkleAnimations = starsRef.current.map((star, index) => {
      const anim = animValues[index];
      return Animated.loop(
        Animated.sequence([
          Animated.timing(anim.opacity, {
            toValue: 0.15,
            duration: star.twinkleSpeed,
            useNativeDriver: true,
          }),
          Animated.timing(anim.opacity, {
            toValue: star.opacity,
            duration: star.twinkleSpeed,
            useNativeDriver: true,
          }),
        ])
      );
    });

    const allAnimations = [...animations, ...twinkleAnimations];
    allAnimations.forEach(anim => anim.start());

    return () => {
      allAnimations.forEach(anim => anim.stop());
    };
  }, []);

  return (
    <View style={styles.container}>
      {starsRef.current.map((star, index) => (
        <Animated.View
          key={index}
          style={[
            styles.star,
            {
              left: star.x,
              width: star.size,
              height: star.size,
              opacity: animValues[index].opacity,
              transform: [
                { translateY: animValues[index].y },
                { scale: animValues[index].scale },
                { translateX: animValues[index].xDrift },
              ],
            },
          ]}
        />
      ))}
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
    backgroundColor: '#05050f',
  },
  star: {
    position: 'absolute',
    borderRadius: 999,
    backgroundColor: '#ffffff',
    shadowColor: '#b4d4ff',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.9,
    shadowRadius: 3,
    elevation: 3,
  },
});
