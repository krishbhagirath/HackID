import HeaderServer from '~/components/HeaderServer';
import HomeContent from '~/components/HomeContent';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <HeaderServer />
      <HomeContent />
    </div>
  );
}
