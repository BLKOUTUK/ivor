import React from 'react'
import { motion } from 'framer-motion'

interface CardData {
  id: number
  title: string
  content: string
  color: string
}

interface FistFormationCardsProps {
  cards: CardData[]
  isFormed: boolean
}

// Helper function to calculate fist formation positions
const getFistPosition = (cardIndex: number) => {
  // Positions to form a raised fist shape (6 cards)
  const positions = [
    // Card 0: Thumb (left side)
    { x: -200, y: 100, rotation: -15 },
    // Card 1: Index finger (top)
    { x: -50, y: -150, rotation: 10 },
    // Card 2: Middle finger (top center)
    { x: 50, y: -180, rotation: -5 },
    // Card 3: Ring finger (top right)
    { x: 150, y: -150, rotation: 15 },
    // Card 4: Pinky (right side)
    { x: 200, y: -100, rotation: 25 },
    // Card 5: Palm/wrist (bottom center)
    { x: 0, y: 150, rotation: 0 }
  ]
  
  return positions[cardIndex] || { x: 0, y: 0, rotation: 0 }
}

const FistFormationCards: React.FC<FistFormationCardsProps> = ({ cards, isFormed }) => {
  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {cards.map((card, index) => {
        const fistPos = getFistPosition(index)
        const gridPosition = {
          x: (index % 3) * 300 - 300,
          y: Math.floor(index / 3) * 200 - 100,
          rotation: 0
        }
        
        const targetPosition = isFormed ? fistPos : gridPosition
        
        return (
          <motion.div
            key={card.id}
            className={`absolute w-64 h-40 ${card.color} rounded-2xl p-6 cursor-pointer shadow-2xl`}
            animate={{
              x: targetPosition.x,
              y: targetPosition.y,
              rotate: targetPosition.rotation,
              scale: isFormed ? 0.8 : 1
            }}
            transition={{
              duration: 1.5,
              ease: "easeInOut",
              delay: index * 0.1
            }}
            whileHover={{ 
              scale: isFormed ? 0.85 : 1.05,
              transition: { duration: 0.2 }
            }}
          >
            <h3 className="text-white font-bold text-lg mb-2">{card.title}</h3>
            <p className="text-white/90 text-sm">{card.content}</p>
          </motion.div>
        )
      })}
      
      {isFormed && (
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-10"
        >
          <div className="text-6xl md:text-8xl">✊🏿</div>
        </motion.div>
      )}
    </div>
  )
}

export default FistFormationCards