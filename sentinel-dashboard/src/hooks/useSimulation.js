/**
 * @fileoverview Custom hook that manages the live simulation state for the dashboard.
 * Handles packet generation, timeline updates, clock ticks, and threat level cycling.
 * Encapsulates all setInterval logic in one place for clean separation of concerns.
 */

import { useState, useEffect, useCallback } from 'react';
import { generatePacket, generateTimeline } from '../data/generators';

/**
 * Manages all real-time simulation state: packets, timeline, KPIs, clock, threat level.
 * @returns {object} Simulation state and control functions
 */
export function useSimulation() {
  const [packets, setPackets] = useState(() => Array.from({ length: 30 }, () => generatePacket()));
  const [timeline, setTimeline] = useState(() => generateTimeline());
  const [attackCount, setAttackCount] = useState(47);
  const [totalPackets, setTotalPackets] = useState(128456);
  const [clock, setClock] = useState(new Date());
  const [threatLevel, setThreatLevel] = useState('MODERATE');

  useEffect(() => {
    /* New packet every 2 seconds */
    const packetInterval = setInterval(() => {
      const packet = generatePacket();
      setPackets((prev) => [packet, ...prev].slice(0, 200));
      setTotalPackets((prev) => prev + 1);
      if (packet.prediction === 'ATTACK') {
        setAttackCount((prev) => prev + 1);
      }
    }, 2000);

    /* Refresh timeline every 30 seconds */
    const timelineInterval = setInterval(() => setTimeline(generateTimeline()), 30000);

    /* Clock tick every second */
    const clockInterval = setInterval(() => setClock(new Date()), 1000);

    /* Threat level shifts every 15 seconds */
    const threatInterval = setInterval(() => {
      const levels = ['LOW', 'MODERATE', 'HIGH', 'CRITICAL'];
      setThreatLevel(levels[Math.floor(Math.random() * 3)]); // weighted toward non-critical
    }, 15000);

    return () => {
      clearInterval(packetInterval);
      clearInterval(timelineInterval);
      clearInterval(clockInterval);
      clearInterval(threatInterval);
    };
  }, []);

  return { packets, timeline, attackCount, totalPackets, clock, threatLevel };
}
