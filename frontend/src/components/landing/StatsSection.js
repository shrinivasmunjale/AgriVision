import Container from '@/components/ui/Container'
import SectionHeading from '@/components/ui/SectionHeading'
import StatCard from '@/components/ui/StatCard'

const stats = [
  { label: 'Confidence Accuracy', value: '97', suffix: '%' },
  { label: 'Disease Classes', value: '10' },
  { label: 'Endpoints', value: '40' },
  { label: 'Report Format', value: '1', suffix: ' PDF' },
]

export default function StatsSection() {
  return (
    <section id="stats" className="py-20 lg:py-28">
      <Container>
        <SectionHeading
          eyebrow="By the numbers"
          title="Built to make a real difference"
          subtitle="A reliable, modern foundation for smarter agriculture."
        />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          {stats.map((s, i) => (
            <StatCard
              key={s.label}
              label={s.label}
              value={s.value}
              suffix={s.suffix}
              delay={i * 0.1}
            />
          ))}
        </div>
      </Container>
    </section>
  )
}