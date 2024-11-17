'use client'

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { toast } from "@/hooks/use-toast"

type LanguageType = 'en' | 'ja'

const translations = {
  en: {
    title: "Project Modification Assistant",
    description: "Enter your desired project modifications, and we'll generate an AI-assisted JSON prompt.",
    inputLabel: "Describe your modifications:",
    inputPlaceholder: "e.g., Add a login feature, Implement dark mode, Create a responsive navbar...",
    generateButton: "Generate JSON Prompt",
    resultTitle: "Generated JSON Prompt",
    copyButton: "Copy to Clipboard",
    processing: "Generating...",
    errorTitle: "Error",
    errorMessage: "An error occurred while generating the JSON prompt.",
    copySuccess: "JSON prompt copied to clipboard!",
  },
  ja: {
    title: "プロジェクト修正アシスタント",
    description: "希望するプロジェクトの修正を入力すると、AI支援によるJSONプロンプトを生成します。",
    inputLabel: "修正内容を記述してください：",
    inputPlaceholder: "例：ログイン機能の追加、ダークモードの実装、レスポンシブなナビバーの作成...",
    generateButton: "JSONプロンプトを生成",
    resultTitle: "生成されたJSONプロンプト",
    copyButton: "クリップボードにコピー",
    processing: "生成中...",
    errorTitle: "エラー",
    errorMessage: "JSONプロンプトの生成中にエラーが発生しました。",
    copySuccess: "JSONプロンプトをクリップボードにコピーしました！",
  }
}

export default function ProjectModification({ language = 'en' }: { language?: LanguageType }) {
  const [userInput, setUserInput] = useState('')
  const [generatedPrompt, setGeneratedPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const t = translations[language]

  const generateJsonPrompt = async () => {
    if (!userInput.trim()) {
      toast({
        title: t.errorTitle,
        description: language === 'en' ? "Please enter your desired modifications." : "修正内容を入力してください。",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    try {
      // In a real application, this would be an API call to your backend
      const response = await fetch('/api/generate-json-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userInput }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate JSON prompt')
      }

      const data = await response.json()
      setGeneratedPrompt(JSON.stringify(data, null, 2))
    } catch (error) {
      console.error('Error generating JSON prompt:', error)
      toast({
        title: t.errorTitle,
        description: t.errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedPrompt).then(() => {
      toast({
        title: t.copySuccess,
        duration: 2000,
      })
    })
  }

  return (
    <Card className="w-full max-w-3xl mx-auto bg-opacity-90 dark:bg-opacity-90">
      <CardHeader>
        <CardTitle>{t.title}</CardTitle>
        <CardDescription>{t.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="userInput" className="text-sm font-medium">
            {t.inputLabel}
          </label>
          <Textarea
            id="userInput"
            placeholder={t.inputPlaceholder}
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            className="min-h-[100px]"
          />
        </div>
        <Button onClick={generateJsonPrompt} disabled={isGenerating} className="w-full">
          {isGenerating ? t.processing : t.generateButton}
        </Button>
        {generatedPrompt && (
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">{t.resultTitle}</h3>
            <ScrollArea className="h-[200px] w-full rounded-md border p-4">
              <pre className="text-sm">{generatedPrompt}</pre>
            </ScrollArea>
            <Button onClick={copyToClipboard} variant="outline" className="w-full">
              {t.copyButton}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}