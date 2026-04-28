/**
 * Logo Oficial MENOSFRANGO 🐣 ➡️ 🦅
 * Frango focado com faixa de suor na cabeça.
 */

interface FrangoLogoProps {
  className?: string;
}

export default function FrangoLogo({ className = "w-24 h-24" }: FrangoLogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      className={className}
    >
      {/* Círculo de Fundo (opcional, pode remover se quiser fundo transparente) */}
      {/*<circle cx="100" cy="100" r="95" className="fill-blue-700 dark:fill-blue-900" />*/}

      {/* Crista do frango */}
      <path
        d="M 100 25 C 115 10, 135 25, 120 45 C 145 35, 155 60, 130 75 Z"
        fill="#EF4444" /* text-red-500 */
      />

      {/* Cabeça */}
      <ellipse cx="100" cy="110" rx="55" ry="60" fill="#FBBF24" /* text-amber-400 */ />

      {/* Faixa de suor (Headband) */}
      <rect x="43" y="75" width="114" height="22" fill="#DC2626" /* text-red-600 */ />
      <line x1="43" y1="75" x2="157" y2="75" stroke="#B91C1C" strokeWidth="2" />
      <line x1="43" y1="97" x2="157" y2="97" stroke="#B91C1C" strokeWidth="2" />

      {/* Nó da faixa (voando para o lado) */}
      <path d="M 155 80 L 185 65 L 175 90 Z" fill="#DC2626" />
      <path d="M 155 90 L 180 105 L 170 80 Z" fill="#B91C1C" />

      {/* Olhos (Expressão de Foco/Raiva) */}
      {/* Fundo Branco */}
      <path d="M 65 105 Q 80 95 90 110 Q 75 115 65 105" fill="white" />
      <path d="M 135 105 Q 120 95 110 110 Q 125 115 135 105" fill="white" />
      
      {/* Sobrancelhas franzidas por cima da faixa */}
      <line x1="60" y1="95" x2="95" y2="110" stroke="#7F1D1D" strokeWidth="6" strokeLinecap="round" />
      <line x1="140" y1="95" x2="105" y2="110" stroke="#7F1D1D" strokeWidth="6" strokeLinecap="round" />
      
      {/* Pupilas encarando o desafio */}
      <circle cx="82" cy="107" r="5" fill="#111827" />
      <circle cx="118" cy="107" r="5" fill="#111827" />

      {/* Bico cerrado (fazendo força) */}
      <path
        d="M 85 125 L 115 125 L 100 145 Z"
        fill="#F59E0B"
        stroke="#D97706"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <line x1="88" y1="130" x2="112" y2="130" stroke="#D97706" strokeWidth="2" />

      {/* Papo vermelho (Wattle) */}
      <path d="M 93 145 Q 85 165 100 160 Q 115 165 107 145 Z" fill="#EF4444" />
    </svg>
  );
}