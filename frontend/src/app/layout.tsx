import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PartSelect QA Assistant',
  description: 'AI-powered question-answering agent for PartSelect appliance parts - specializing in dishwashers and refrigerators',
  keywords: 'appliance parts, dishwasher, refrigerator, repair, PartSelect, AI assistant',
  authors: [{ name: 'Akhil Reddy' }],
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}