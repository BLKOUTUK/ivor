import React, { useState } from 'react'
import { motion } from 'framer-motion'

interface QuizQuestion {
  question: string
  answers: string[]
  correctAnswer?: number
}

interface QuizSlide {
  type: 'quiz'
  title: string
  questions: QuizQuestion[]
  results?: {
    [key: string]: {
      title: string
      description: string
      color: string
    }
  }
}

interface QuizComponentProps {
  slide: QuizSlide
}

const QuizComponent: React.FC<QuizComponentProps> = ({ slide }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([])
  const [showResults, setShowResults] = useState(false)
  const [isStarted, setIsStarted] = useState(false)

  const handleAnswerSelect = (answerIndex: number) => {
    const newAnswers = [...selectedAnswers]
    newAnswers[currentQuestion] = answerIndex
    setSelectedAnswers(newAnswers)
    
    // Auto-advance after a brief delay
    setTimeout(() => {
      if (currentQuestion < slide.questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1)
      } else {
        setShowResults(true)
      }
    }, 1000)
  }

  const calculateResult = () => {
    if (!slide.results) return null
    
    // Simple scoring logic - can be enhanced
    const score = selectedAnswers.reduce((sum, answer) => sum + answer, 0)
    const resultKeys = Object.keys(slide.results)
    const resultIndex = Math.min(Math.floor(score / 2), resultKeys.length - 1)
    return slide.results[resultKeys[resultIndex]]
  }

  const resetQuiz = () => {
    setCurrentQuestion(0)
    setSelectedAnswers([])
    setShowResults(false)
    setIsStarted(true)
  }

  if (!isStarted) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl"
        >
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            {slide.title}
          </h2>
          <p className="text-xl text-white/80 mb-8">
            Discover your liberation pathway through community connection
          </p>
          <motion.button
            onClick={() => setIsStarted(true)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-full text-lg font-semibold"
          >
            Begin Journey
          </motion.button>
        </motion.div>
      </div>
    )
  }

  if (showResults) {
    const result = calculateResult()
    
    return (
      <div className="flex flex-col items-center justify-center h-full text-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-2xl"
        >
          <h3 className="text-3xl font-bold text-white mb-4">
            Your Liberation Pathway
          </h3>
          {result && (
            <div className={`p-6 rounded-2xl bg-gradient-to-br ${result.color} mb-6`}>
              <h4 className="text-2xl font-bold text-white mb-3">{result.title}</h4>
              <p className="text-white/90">{result.description}</p>
            </div>
          )}
          <motion.button
            onClick={resetQuiz}
            whileHover={{ scale: 1.05 }}
            className="bg-white/20 backdrop-blur-sm text-white px-6 py-3 rounded-full"
          >
            Take Again
          </motion.button>
        </motion.div>
      </div>
    )
  }

  const question = slide.questions[currentQuestion]
  
  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <motion.div
        key={currentQuestion}
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -50 }}
        className="max-w-3xl w-full"
      >
        <div className="text-center mb-8">
          <div className="text-white/60 mb-2">
            Question {currentQuestion + 1} of {slide.questions.length}
          </div>
          <h3 className="text-2xl md:text-3xl font-bold text-white mb-8">
            {question.question}
          </h3>
        </div>
        
        <div className="grid gap-4">
          {question.answers.map((answer, index) => (
            <motion.button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-4 bg-white/10 backdrop-blur-sm rounded-xl text-white text-left hover:bg-white/20 transition-all duration-300"
            >
              {answer}
            </motion.button>
          ))}
        </div>
        
        <div className="mt-8 w-full bg-white/20 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestion + 1) / slide.questions.length) * 100}%` }}
          />
        </div>
      </motion.div>
    </div>
  )
}

export default QuizComponent