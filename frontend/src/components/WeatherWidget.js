'use client'

import { useEffect, useState } from 'react'
import { CloudSun, Droplets, Wind, Thermometer, MapPin, RefreshCw } from 'lucide-react'
import { miscAPI } from '@/lib/api'

// Open-Meteo WMO weather codes -> (label, emoji)
const codeMap = {
  0: ['Clear sky', '☀️'], 1: ['Mostly clear', '🌤️'], 2: ['Partly cloudy', '⛅'],
  3: ['Overcast', '☁️'], 45: ['Foggy', '🌫️'], 48: ['Fog', '🌫️'],
  51: ['Light drizzle', '🌦️'], 53: ['Drizzle', '🌦️'], 55: ['Heavy drizzle', '🌧️'],
  61: ['Light rain', '🌦️'], 63: ['Rain', '🌧️'], 65: ['Heavy rain', '🌧️'],
  71: ['Light snow', '🌨️'], 73: ['Snow', '❄️'], 75: ['Heavy snow', '❄️'],
  80: ['Light showers', '🌦️'], 81: ['Showers', '🌧️'], 82: ['Heavy showers', '⛈️'],
  95: ['Thunderstorm', '⛈️'], 96: ['Storm w/ hail', '⛈️'], 99: ['Storm w/ hail', '⛈️'],
}

export default function WeatherWidget() {
  const [weather, setWeather] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchWeather = (lat, lon) => {
    setLoading(true)
    setError('')
    miscAPI
      .weather(lat, lon)
      .then((res) => setWeather(res.data))
      .catch(() => setError('Weather unavailable'))
      .finally(() => setLoading(false))
  }

  const autoLocate = () => {
    if (!navigator.geolocation) {
      // Default to a farming-friendly location
      fetchWeather(19.076, 72.8777)
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => fetchWeather(pos.coords.latitude, pos.coords.longitude),
      () => fetchWeather(19.076, 72.8777)
    )
  }

  useEffect(() => {
    autoLocate()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (loading && !weather) {
    return (
      <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle flex items-center justify-center h-full min-h-[10rem]">
        <RefreshCw className="w-6 h-6 text-primary-400 animate-spin" />
      </div>
    )
  }

  if (error && !weather) {
    return (
      <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle text-text-secondary text-sm">
        {error}
      </div>
    )
  }

  const cur = weather?.current
  const daily0 = weather?.daily && {
    max: weather.daily.temperature_2m_max?.[0],
    min: weather.daily.temperature_2m_min?.[0],
    precip: weather.daily.precipitation_probability_max?.[0],
  }
  const wc = cur?.weather_code
  const [label, emoji] = codeMap[wc] || ['Unknown', '🌡️']

  return (
    <div className="bg-surface-card rounded-2xl p-6 border border-border-subtle">
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 font-semibold text-text-primary">
          <CloudSun className="w-5 h-5 text-primary-400" /> Local Weather
        </h3>
        <button
          onClick={autoLocate}
          title="Refetch location"
          className="text-text-secondary hover:text-primary-400 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {cur && (
        <>
          <div className="flex items-center gap-4 mb-4">
            <span className="text-5xl">{emoji}</span>
            <div>
              <p className="text-3xl font-bold text-text-primary">
                {Math.round(cur.temperature_2m)}°C
              </p>
              <p className="text-text-secondary">{label}</p>
            </div>
            <span className="ml-auto inline-flex items-center gap-1 text-xs text-text-secondary px-2 py-1 bg-surface-base rounded-full">
              <MapPin className="w-3 h-3" /> Live
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center mb-4">
            {[
              { icon: Thermometer, label: 'Feels', value: `${Math.round(cur.apparent_temperature)}°` },
              { icon: Droplets, label: 'Humidity', value: `${cur.relative_humidity_2m}%` },
              { icon: Wind, label: 'Wind', value: `${Math.round(cur.wind_speed_10m)} km/h` },
            ].map((s, i) => {
              const Icon = s.icon
              return (
                <div key={i} className="bg-surface-base rounded-xl p-3">
                  <Icon className="w-4 h-4 text-primary-400 mx-auto mb-1" />
                  <p className="text-xs text-text-secondary">{s.label}</p>
                  <p className="text-sm font-semibold text-text-primary">{s.value}</p>
                </div>
              )
            })}
          </div>

          {daily0 && (
            <div className="pt-3 border-t border-border-subtle text-xs text-text-secondary flex justify-between">
              <span>Today: {Math.round(daily0.min)}° – {Math.round(daily0.max)}°</span>
              <span>Rain: {daily0.precip ?? 0}%</span>
            </div>
          )}
        </>
      )}
    </div>
  )
}