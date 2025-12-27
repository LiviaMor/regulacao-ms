import { Tabs } from 'expo-router';
import React from 'react';

import { HapticTab } from '@/components/haptic-tab';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#004A8D', // Azul SES-GO
        tabBarInactiveTintColor: '#666',
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: {
          backgroundColor: '#FFF',
          borderTopWidth: 1,
          borderTopColor: '#E0E0E0',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color }) => <IconSymbol size={22} name="chart.bar.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Hospital',
          tabBarIcon: ({ color }) => <IconSymbol size={22} name="cross.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="consulta"
        options={{
          title: 'Consulta',
          tabBarIcon: ({ color }) => <IconSymbol size={22} name="magnifyingglass" color={color} />,
        }}
      />
      <Tabs.Screen
        name="regulacao"
        options={{
          title: 'Regulação',
          tabBarIcon: ({ color }) => <IconSymbol size={22} name="list.clipboard.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="transferencia"
        options={{
          title: 'Transferência',
          tabBarIcon: ({ color }) => <IconSymbol size={22} name="truck.box.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}
