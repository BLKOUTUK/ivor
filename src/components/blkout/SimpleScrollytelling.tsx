import React from 'react'
import { motion } from 'framer-motion'
import HorizontalProjects from './HorizontalProjects'

const SimpleScrollytelling: React.FC = () => {
  const slides = [
    {
      id: 'welcome-video',
      type: 'video',
      videoSrc: '/images/welcomevidfinal.webm',
      height: '100vh'
    },
    {
      id: 'who',
      type: 'image',
      imageSrc: '/images/WHO.png',
      title: 'WHO',
      height: '40vh'
    },
    {
      id: 'well-defined',
      type: 'image',
      imageSrc: '/images/welldef2.png',
      title: 'WELL DEFINED',
      height: '100vh'
    },
    {
      id: 'black',
      type: 'image',
      imageSrc: '/images/black2.png',
      title: 'BLACK?',
      height: '100vh'
    },
    {
      id: 'queer',
      type: 'image',
      imageSrc: '/images/queer2.png',
      title: 'QUEER',
      height: '100vh'
    },
    {
      id: 'male',
      type: 'image',
      imageSrc: '/images/men2.png',
      title: 'MALE*',
      height: '100vh'
    },
    {
      id: 'out',
      type: 'image',
      imageSrc: '/images/out2.png',
      title: 'OUT',
      height: '100vh'
    },
    {
      id: 'work',
      type: 'image',
      imageSrc: '/images/the work.png',
      title: 'THE WORK',
      height: '40vh'
    },
    {
      id: 'liberation',
      type: 'image',
      imageSrc: '/images/liberation.png',
      title: 'LIBERATION',
      height: '100vh'
    }
  ]

  return (
    <div className="min-h-screen bg-black">
      {/* BLKOUT Pride 2025 Logo Header */}
      <header className="bg-black py-8 relative z-50">
        <div className="flex justify-center">
          <img 
            src="/images/BLKOUTpride2025.png" 
            alt="BLKOUT Pride 2025" 
            className="w-1/3 max-w-md h-auto"
          />
        </div>
      </header>

      {/* Slides Container */}
      <div className="relative">
        {slides.map((slide, index) => (
          <motion.section
            key={slide.id}
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            viewport={{ once: false, margin: "-10%", amount: 0.3 }}
            className="relative w-full flex items-center justify-center bg-black"
            style={{ minHeight: slide.height || '100vh' }}
          >
            {slide.type === 'video' ? (
              <div className="w-full h-screen relative">
                <video
                  className="w-full h-full object-contain"
                  autoPlay
                  muted
                  loop
                  playsInline
                >
                  <source src={slide.videoSrc} type="video/webm" />
                  Your browser does not support the video tag.
                </video>
                
                {/* Rising text animations during welcome video */}
                <div className="absolute inset-0 pointer-events-none z-10">
                  <motion.img 
                    src="/images/USALL.png"
                    initial={{ y: "100%", opacity: 0 }}
                    animate={{ 
                      y: ["100%", "0%", "0%", "-100%"],
                      opacity: [0, 1, 1, 0]
                    }}
                    transition={{ 
                      duration: 6,
                      times: [0, 0.4, 0.7, 1],
                      delay: 15,
                      ease: "easeOut"
                    }}
                    className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1/2 max-w-md"
                  />
                  <motion.img 
                    src="/images/ALLOFUS.png" 
                    initial={{ y: "100%", opacity: 0 }}
                    animate={{ 
                      y: ["100%", "0%", "0%", "-100%"],
                      opacity: [0, 1, 1, 0]
                    }}
                    transition={{ 
                      duration: 6,
                      times: [0, 0.4, 0.7, 1],
                      delay: 20,
                      ease: "easeOut"
                    }}
                    className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1/2 max-w-md"
                  />
                </div>
              </div>
            ) : (
              <div className="w-full relative flex items-center justify-center" style={{ height: slide.height || '100vh' }}>
                <img
                  src={slide.imageSrc}
                  alt={slide.title}
                  className="max-w-full max-h-full object-contain"
                />
              </div>
            )}
            
            {/* Screen reader accessibility */}
            <div className="sr-only">
              <h2>{slide.title || 'Welcome Video'}</h2>
            </div>
          </motion.section>
        ))}
        
        {/* Horizontal Projects Section */}
        <HorizontalProjects />
        
        {/* Platform Access Section */}
        <motion.section
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          viewport={{ once: false, amount: 0.3 }}
          className="relative w-full flex items-center justify-center bg-black py-20"
        >
          <div className="text-center">
            <h2 className="text-4xl md:text-6xl font-bold text-white mb-8">
              ENTER THE <span className="text-orange-500">PLATFORM</span>
            </h2>
            <p className="text-xl text-white/80 mb-12 max-w-2xl mx-auto">
              Access community tools: Newsroom, IVOR AI, Events, and Liberation Resources
            </p>
            <div className="space-y-4">
              <a 
                href="http://localhost:8000/newsroom"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gradient-to-r from-orange-500 to-pink-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-orange-600 hover:to-pink-600 transition-all duration-300 transform hover:scale-105 mx-2"
              >
                📰 Newsroom
              </a>
              <a 
                href="http://localhost:8000/chat"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gradient-to-r from-blue-500 to-purple-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300 transform hover:scale-105 mx-2"
              >
                🤖 Chat with IVOR
              </a>
              <a 
                href="http://localhost:8000/community/dashboard"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-gradient-to-r from-green-500 to-teal-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:from-green-600 hover:to-teal-600 transition-all duration-300 transform hover:scale-105 mx-2"
              >
                🏠 Community Dashboard
              </a>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  )
}

export default SimpleScrollytelling