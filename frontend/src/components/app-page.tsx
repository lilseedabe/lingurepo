'use client'

import React, { useState, useEffect, useRef } from 'react'
import { ThemeProvider, useTheme } from 'next-themes'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { toast } from "@/hooks/use-toast"
import ProjectModification from './project-modification'

type FileType = { name: string; type: 'file' | 'directory'; path: string; children?: FileType[] };
type FileHistoryType = { date: string; author: string; message: string };

const translations = {
  en: {
    description: "GitHub Repository Analysis and Design Document Generator",
    repoName: "Repository Name",
    branchName: "Branch Name",
    analyze: "Analyze Repository",
    processing: "Processing...",
    files: "Files",
    template: "Design Template",
    editor: "Code Editor",
    repoFiles: "Repository Files",
    generatedTemplate: "Generated Design Document",
    export: "Export",
    templateValid: "Template is valid",
    templateInvalid: "Template is invalid",
    selectFile: "Select a file to edit",
    hideDiff: "Hide Diff",
    showDiff: "Show Diff",
    saveChanges: "Save Changes",
    diffView: "Diff View",
    oldLine: "Old line",
    newLine: "New line",
    selectFilePrompt: "Select a file from the Files tab to edit its content.",
    startNewAnalysis: "Start New Analysis",
    viewFileHistory: "View File History",
    fileHistory: "File History",
    recentChanges: "Recent changes for",
    analysisProgress: "Analysis Progress",
    documentStructure: "Document Structure",
    aiInsights: "AI Insights",
    selectFilesToAnalyze: "Select Files to Analyze",
    analyzeSelected: "Analyze Selected Files",
    step1: "Step 1: Enter Repository Details",
    step2: "Step 2: Select Files to Analyze",
    step3: "Step 3: Review Analysis Results",
    fetchingFiles: "Fetching repository files...",
    analyzingFiles: "Analyzing selected files...",
    analysisComplete: "Analysis Complete!",
    viewResults: "View Results",
    noFilesSelected: "No files selected. Please select at least one file to analyze.",
    selectAll: "Select All",
    deselectAll: "Deselect All",
    noFilesFound: "No files found.",
    mainPage: "Repository Analysis",
    modificationPage: "Project Modification",
  },
  ja: {
    description: "GitHubリポジトリ分析と設計書生成ツール",
    repoName: "リポジトリ名",
    branchName: "ブランチ名",
    analyze: "リポジトリを分析",
    processing: "処理中...",
    files: "ファイル",
    template: "設計テンプレート",
    editor: "コードエディタ",
    repoFiles: "リポジトリファイル",
    generatedTemplate: "生成された設計書",
    export: "エクスポート",
    templateValid: "テンプレートは有効です",
    templateInvalid: "テンプレートは無効です",
    selectFile: "編集するファイルを選択",
    hideDiff: "差分を隠す",
    showDiff: "差分を表示",
    saveChanges: "変更を保存",
    diffView: "差分ビュー",
    oldLine: "古い行",
    newLine: "新しい行",
    selectFilePrompt: "ファイルタブからファイルを選択して内容を編集してください。",
    startNewAnalysis: "新しい分析を開始",
    viewFileHistory: "ファイル履歴を表示",
    fileHistory: "ファイル履歴",
    recentChanges: "最近の変更：",
    analysisProgress: "分析の進捗",
    documentStructure: "文書構造",
    aiInsights: "AI洞察",
    selectFilesToAnalyze: "分析するファイルを選択",
    analyzeSelected: "選択したファイルを分析",
    step1: "ステップ1: リポジトリ詳細を入力",
    step2: "ステップ2: 分析するファイルを選択",
    step3: "ステップ3: 分析結果を確認",
    fetchingFiles: "リポジトリファイルを取得中...",
    analyzingFiles: "選択されたファイルを分析中...",
    analysisComplete: "分析完了！",
    viewResults: "結果を表示",
    noFilesSelected: "ファイルが選択されていません。少なくとも1つのファイルを選択してください。",
    selectAll: "全て選択",
    deselectAll: "全て解除",
    noFilesFound: "ファイルが見つかりませんでした。",
    mainPage: "リポジトリ分析",
    modificationPage: "プロジェクト修正",
  }
}

function ThemeToggle() {
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
        </svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
        </svg>
      )}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}

function LanguageToggle({ language, setLanguage }: { language: string; setLanguage: (lang: string) => void }) {
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setLanguage(language === 'ja' ? 'en' : 'ja')}
      aria-label={language === 'en' ? 'Switch to Japanese' : '英語に切り替え'}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="w-4 h-4"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
      </svg>
    </Button>
  )
}

function ParticleAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { theme } = useTheme()

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth
      canvas.height = canvas.offsetHeight
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    const points: { x: number; y: number; vx: number; vy: number }[] = []
    const pointCount = 50
    const maxDistance = 100

    const createPoint = () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5
    })

    const glowLine = () => ({
      start: Math.floor(Math.random() * points.length),
      end: Math.floor(Math.random() * points.length),
      progress: 0,
      duration: Math.random() * 1000 + 500, // 0.5秒から1.5秒のランダムな持続時間
    });

    let glowingLines: ReturnType<typeof glowLine>[] = [];

    for (let i = 0; i < pointCount; i++) {
      points.push(createPoint())
    }

    let animationId: number;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      points.forEach((point) => {
        point.x += point.vx
        point.y += point.vy

        if (point.x < 0 || point.x > canvas.width) point.vx *= -1
        if (point.y < 0 || point.y > canvas.height) point.vy *= -1

        points.forEach((otherPoint) => {
          const dx = point.x - otherPoint.x
          const dy = point.y - otherPoint.y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < maxDistance) {
            ctx.beginPath()
            ctx.moveTo(point.x, point.y)
            ctx.lineTo(otherPoint.x, otherPoint.y)
            const opacity = 1 - distance / maxDistance
            ctx.strokeStyle = theme === 'dark'
              ? `rgba(135, 206, 250, ${opacity * 0.3})` // ライトスカイブルー
              : `rgba(0, 191, 255, ${opacity * 0.2})`; // ディープスカイブルー
            ctx.lineWidth = 1
            ctx.stroke()
          }
        })

        ctx.beginPath()
        ctx.arc(point.x, point.y, 1, 0, Math.PI * 2)
        ctx.fillStyle = theme === 'dark'
          ? `rgba(255, 255, 255, 0.5)`
          : `rgba(0, 0, 0, 0.3)`
        ctx.fill()
      })

      // ランダムに新しい光る線を追加
      if (Math.random() < 0.05) { // 5%の確率で新しい線を追加
        glowingLines.push(glowLine());
      }

      // 光る線を描画・更新
      glowingLines = glowingLines.filter(line => {
        const startPoint = points[line.start]
        const endPoint = points[line.end]
        const gradient = ctx.createLinearGradient(startPoint.x, startPoint.y, endPoint.x, endPoint.y);
        
        // テーマに応じて色を変更
        const glowColor = theme === 'dark'
          ? `rgba(135, 206, 250, ${0.7 * Math.sin(Math.PI * line.progress)})` // ライトスカイブルー
          : `rgba(0, 191, 255, ${0.5 * Math.sin(Math.PI * line.progress)})`; // ディープスカイブルー

        gradient.addColorStop(0, `rgba(255, 255, 255, 0)`);
        gradient.addColorStop(0.5, glowColor);
        gradient.addColorStop(1, `rgba(255, 255, 255, 0)`);

        ctx.beginPath()
        ctx.moveTo(startPoint.x, startPoint.y)
        ctx.lineTo(endPoint.x, endPoint.y)
        ctx.strokeStyle = gradient
        ctx.lineWidth = 2
        ctx.stroke()

        line.progress += 1 / (line.duration / 16) // 60FPSを想定
        return line.progress < 1
      })

      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      cancelAnimationFrame(animationId)
    }
  }, [theme])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none"
      aria-hidden="true"
    />
  )
}

export function BlockPage() {
  const [language, setLanguage] = useState('en')
  const t = translations[language as keyof typeof translations]
  const [repoName, setRepoName] = useState('')
  const [branchName, setBranchName] = useState('')
  const [isFetchingFiles, setIsFetchingFiles] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [files, setFiles] = useState<FileType[]>([])
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [finalDocument, setFinalDocument] = useState('')
  const [isValid, setIsValid] = useState<boolean | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState('')
  const [fileHistory, setFileHistory] = useState<FileHistoryType[]>([])
  const [showDiff, setShowDiff] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [documentStructure, setDocumentStructure] = useState<any>(null)
  const [aiInsights, setAiInsights] = useState<{ en: string; ja: string }>({
    en: '',
    ja: ''
  })
  const [currentStep, setCurrentStep] = useState(1)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [allSelected, setAllSelected] = useState(false)
  const [currentPage, setCurrentPage] = useState<'main' | 'modification'>('main')

  // 新しい関数: リポジトリのファイルツリーを取得
  const fetchListRepoFiles = async () => {
    try {
      setIsFetchingFiles(true)
      const response = await fetch('http://localhost:8000/list-repo-files', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ repo_name: repoName, branch_name: branchName })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || (language === 'en' ? "Failed to fetch repository files." : "リポジトリファイルの取得に失敗しました。"))
      }

      const data = await response.json()
      setFiles(data.files)
      setCurrentStep(2)
      toast({
        title: language === 'en' ? "Files fetched successfully." : "ファイルを正常に取得しました。",
        description: language === 'en' ? "You can now select files to analyze." : "ファイルを選択して分析を開始できます。",
      })
    } catch (error: any) {
      console.error('Error fetching repository files:', error)
      toast({
        title: language === 'en' ? "Error" : "エラー",
        description: error.message || (language === 'en' ? "An error occurred while fetching repository files." : "リポジトリファイルの取得中にエラーが発生しました。"),
        variant: "destructive",
      })
    } finally {
      setIsFetchingFiles(false)
    }
  }

  // 新しい関数: 選択されたファイルを解析
  const fetchGenerateDesignDocument = async () => {
    try {
      setIsAnalyzing(true)
      const response = await fetch('http://localhost:8000/generate-design-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ repo_name: repoName, branch_name: branchName, selected_files: selectedFiles })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || (language === 'en' ? "Failed to generate design document." : "設計書の生成に失敗しました。"))
      }

      const data = await response.json()
      // data.final_documents は統合された設計書
      const combinedDocuments = Object.entries(data.final_documents)
        .map(([file, doc]) => `## ${file}\n${JSON.stringify(doc, null, 2)}`)
        .join('\n\n')
      setFinalDocument(combinedDocuments)
      setAnalysisProgress(100)
      setAnalysisComplete(true)
      toast({
        title: language === 'en' ? t.analysisComplete : t.analysisComplete,
        description: language === 'en' ? t.viewResults : t.viewResults,
      })
      setCurrentStep(3)
    } catch (error: any) {
      console.error('Error generating design document:', error)
      toast({
        title: language === 'en' ? "Error" : "エラー",
        description: error.message || (language === 'en' ? "An error occurred while generating the design document." : "設計書の生成中にエラーが発生しました。"),
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repoName || !branchName) {
      toast({
        title: language === 'en' ? "Please enter both repository name and branch name." : "リポジトリ名とブランチ名を入力してください。",
        description: language === 'en' ? "Both fields are required." : "両方のフィールドを埋めてください。",
        variant: "destructive",
      });
      return
    }

    setIsFetchingFiles(true)
    setAnalysisProgress(0)
    setCurrentStep(1)

    try {
      toast({
        title: language === 'en' ? t.fetchingFiles : t.fetchingFiles,
        description: language === 'en' ? t.processing : t.processing,
      })

      // リポジトリのファイルツリーを取得
      await fetchListRepoFiles()

    } catch (error: any) {
      console.error('Error during fetching files:', error)
      toast({
        title: language === 'en' ? "Error" : "エラー",
        description: error.message || (language === 'en' ? "An error occurred during file fetching." : "ファイル取得中にエラーが発生しました。"),
        variant: "destructive",
      })
      setIsFetchingFiles(false)
    }
  }

  const handleExport = () => {
    const blob = new Blob([finalDocument], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'lingurepo-design-document.json'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleSelectAll = () => {
    if (allSelected) {
      setSelectedFiles([]);
    } else {
      // すべてのファイルのパスを選択
      const allFilePaths = getAllFilePaths(files)
      setSelectedFiles(allFilePaths);
    }
    setAllSelected(!allSelected);
  };

  // すべてのファイルパスを取得する再帰関数
  const getAllFilePaths = (files: FileType[]): string[] => {
    let paths: string[] = [];
    files.forEach(file => {
      if (file.type === 'file') {
        paths.push(file.path);
      } else if (file.type === 'directory' && file.children) {
        paths = paths.concat(getAllFilePaths(file.children));
      }
    });
    return paths;
  }

  const renderFileTree = (files: FileType[], depth = 0) => {
    return (
      <ul className={`space-y-1 ${depth > 0 ? 'ml-4' : ''}`}>
        {files.map((file) => (
          <li key={file.path} className="flex items-center space-x-2">
            <span className="w-4 h-4 text-xs">
              {file.type === 'directory' ? '📁' : '📄'}
            </span>
            {file.type === 'file' && (
              <Checkbox
                id={`file-${file.path}`}
                checked={selectedFiles.includes(file.path)}
                onCheckedChange={(checked) => handleFileCheckboxChange(file.path, checked as boolean)}
              />
            )}
            {file.type === 'directory' ? (
              // ディレクトリの場合は名前のみ表示
              <span className="text-sm cursor-pointer hover:underline">{file.name}</span>
            ) : (
              // ファイルの場合はラベルを表示
              <label
                htmlFor={`file-${file.path}`}
                className="text-sm cursor-pointer hover:underline"
                onClick={() => handleFileSelect(file.path)}
              >
                {file.name}
              </label>
            )}
            {/* 再帰的にディレクトリ内のファイルを表示 */}
            {file.type === 'directory' && file.children && (
              <div className="ml-4">
                {renderFileTree(file.children, depth + 1)}
              </div>
            )}
          </li>
        ))}
      </ul>
    )
  }

  const handleFileCheckboxChange = (filePath: string, checked: boolean) => {
    setSelectedFiles(prev => {
      const newSelection = checked
        ? [...prev, filePath]
        : prev.filter(f => f !== filePath);
      // 全て選択されているかどうかを更新
      const allFilePaths = getAllFilePaths(files)
      setAllSelected(newSelection.length === allFilePaths.length);
      return newSelection;
    });
  }

  const handleFileSelect = (filePath: string) => {
    setSelectedFile(filePath)
    // ファイルの履歴や内容を表示する場合はここで設定
    // ここではシミュレーションとしてプレースホルダーを設定
    setFileContent(`# ${filePath}\n\nThis is a placeholder content for ${filePath}. In a real application, this would be fetched from the repository.`)
    setFileHistory([
      { date: '2023-05-01', author: 'John Doe', message: 'Initial commit' },
      { date: '2023-05-15', author: 'Jane Smith', message: 'Updated file structure' },
    ])
  }

  const handleAnalyzeSelected = async () => {
    if (selectedFiles.length === 0) {
      toast({
        title: language === 'en' ? t.noFilesSelected : t.noFilesSelected,
        description: language === 'en' ? t.selectFilesToAnalyze : t.selectFilesToAnalyze,
        variant: "destructive",
      })
      return
    }

    setIsAnalyzing(true)
    setAnalysisProgress(0)
    setCurrentStep(2)

    try {
      toast({
        title: language === 'en' ? t.analyzingFiles : t.analyzingFiles,
        description: language === 'en' ? t.processing : t.processing,
      })

      // 選択されたファイルを解析
      await fetchGenerateDesignDocument()

    } catch (error: any) {
      console.error('Error during analysis:', error)
      toast({
        title: language === 'en' ? "Error" : "エラー",
        description: error.message || (language === 'en' ? "An error occurred while analyzing the selected files." : "選択されたファイルの分析中にエラーが発生しました。"),
        variant: "destructive",
      })
      setIsAnalyzing(false)
    }
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <div className="min-h-screen w-screen h-screen flex flex-col overflow-hidden bg-background text-foreground">
        <div className="flex-1 overflow-auto">
          <div className="container mx-auto p-4">
            <Card className="w-full max-w-6xl mx-auto bg-opacity-90 dark:bg-opacity-90">
              <div className="relative">
                <ParticleAnimation />
                <div className="relative z-10">
                  <CardHeader className="flex flex-col items-start space-y-2">
                    <div className="flex items-center space-x-4">
                      <svg
                        width="48"
                        height="48"
                        viewBox="0 0 200 200"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-12 h-12"
                      >
                        <path
                          d="M60 40V160"
                          stroke="currentColor"
                          strokeWidth="8"
                          strokeLinecap="round"
                        />
                        <path
                          d="M40 60H160"
                          stroke="currentColor"
                          strokeWidth="8"
                          strokeLinecap="round"
                        />
                        <path
                          d="M120 60C140 60 160 80 160 100C160 120 140 140 120 160"
                          stroke="currentColor"
                          strokeWidth="8"
                          strokeLinecap="round"
                          fill="none"
                        />
                        <g transform="translate(90, 100)">
                          <ellipse
                            cx="-15"
                            cy="-5"
                            rx="3"
                            ry="4"
                            fill="currentColor"
                          />
                          <ellipse
                            cx="5"
                            cy="-5"
                            rx="3"
                            ry="4"
                            fill="currentColor"
                          />
                          <path
                            d="M-20 10C-20 20 20 20 20 10"
                            stroke="currentColor"
                            strokeWidth="4"
                            strokeLinecap="round"
                            fill="none"
                          />
                        </g>
                      </svg>
                      <h1 className="text-3xl font-bold">LinguRepo</h1>
                    </div>
                    <CardDescription className="text-lg">{t.description}</CardDescription>
                    <div className="flex gap-2 self-end">
                      <div className="flex space-x-2 mb-4">
                        <Button
                          variant={currentPage === 'main' ? "default" : "outline"}
                          onClick={() => setCurrentPage('main')}
                        >
                          {t.mainPage}
                        </Button>
                        <Button
                          variant={currentPage === 'modification' ? "default" : "outline"}
                          onClick={() => setCurrentPage('modification')}
                        >
                          {t.modificationPage}
                        </Button>
                      </div>
                      <ThemeToggle />
                      <LanguageToggle language={language} setLanguage={setLanguage} />
                    </div>
                  </CardHeader>
                  <CardContent className="p-6 md:p-8">
                    {currentPage === 'main' ? (
                      <ScrollArea className="h-full pr-4">
                        <div className="space-y-6">
                          {/* Step 1: Enter Repository Details */}
                          <div className="space-y-2">
                            <h2 className="text-xl font-semibold">{t.step1}</h2>
                            <form onSubmit={handleSubmit} className="space-y-4">
                              <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4 mb-4 p-2">
                                <Input
                                  placeholder={t.repoName}
                                  value={repoName}
                                  onChange={(e) => setRepoName(e.target.value)}
                                  className="flex-grow rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-full"
                                />
                                <Input
                                  placeholder={t.branchName}
                                  value={branchName}
                                  onChange={(e) => setBranchName(e.target.value)}
                                  className="flex-grow rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 max-w-full"
                                />
                              </div>
                              <Button type="submit" disabled={isFetchingFiles} className="w-full">
                                {isFetchingFiles ? t.processing : t.analyze}
                              </Button>
                            </form>
                          </div>

                          {/* Step 2: Select Files to Analyze */}
                          <div className="space-y-2">
                            <h2 className="text-xl font-semibold">{t.step2}</h2>
                            <Card>
                              <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                  <span>{t.selectFilesToAnalyze}</span>
                                  <Button 
                                    onClick={handleSelectAll} 
                                    size="sm"
                                    variant="outline"
                                  >
                                    {allSelected ? t.deselectAll : t.selectAll}
                                  </Button>
                                </CardTitle>
                              </CardHeader>
                              <CardContent>
                                <ScrollArea className="h-[400px]">
                                  {files.length > 0 ? renderFileTree(files) : (
                                    <p>{t.noFilesFound}</p>
                                  )}
                                </ScrollArea>
                              </CardContent>
                              <CardFooter>
                                <Button 
                                  onClick={handleAnalyzeSelected} 
                                  disabled={isAnalyzing || selectedFiles.length === 0}
                                  className="w-full"
                                >
                                  {isAnalyzing ? t.processing : t.analyzeSelected}
                                </Button>
                              </CardFooter>
                            </Card>
                          </div>

                          {/* Step 3: Review Analysis Results */}
                          <div className="space-y-2">
                            <h2 className="text-xl font-semibold">{t.step3}</h2>
                            <Tabs defaultValue="template">
                              <TabsList>
                                <TabsTrigger value="template">{t.template}</TabsTrigger>
                                <TabsTrigger value="structure">{t.documentStructure}</TabsTrigger>
                                <TabsTrigger value="insights">{t.aiInsights}</TabsTrigger>
                              </TabsList>
                              <TabsContent value="template">
                                <Card>
                                  <CardHeader>
                                    <CardTitle className="flex items-center justify-between">
                                      <span>{t.generatedTemplate}</span>
                                      <Button onClick={handleExport} size="sm">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 mr-2">
                                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                                        </svg>
                                        {t.export}
                                      </Button>
                                    </CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <ScrollArea className="h-[300px]">
                                      <pre className="text-sm whitespace-pre-wrap break-words">{finalDocument}</pre>
                                    </ScrollArea>
                                  </CardContent>
                                </Card>
                              </TabsContent>
                              <TabsContent value="structure">
                                <Card>
                                  <CardHeader>
                                    <CardTitle>{t.documentStructure}</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <ScrollArea className="h-[300px]">
                                      <pre className="text-sm">{JSON.stringify(documentStructure, null, 2)}</pre>
                                    </ScrollArea>
                                  </CardContent>
                                </Card>
                              </TabsContent>
                              <TabsContent value="insights">
                                <Card>
                                  <CardHeader>
                                    <CardTitle>{t.aiInsights}</CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <ScrollArea className="h-[300px]">
                                      <p className="text-sm">{aiInsights[language as keyof typeof aiInsights]}</p>
                                    </ScrollArea>
                                  </CardContent>
                                </Card>
                              </TabsContent>
                            </Tabs>
                          </div>

                          {/* Progress Bar */}
                          {(isFetchingFiles || isAnalyzing) && (
                            <div className="mt-4">
                              <h3 className="text-lg font-semibold mb-2">{t.analysisProgress}</h3>
                              <Progress 
                                value={isFetchingFiles ? 100 : analysisProgress} 
                                className="w-full" 
                              />
                            </div>
                          )}

                          {/* Analysis Complete Alert */}
                          {analysisComplete && (
                            <Alert className="mt-4">
                              <AlertTitle>{t.analysisComplete}</AlertTitle>
                              <AlertDescription>
                                {t.viewResults}
                              </AlertDescription>
                            </Alert>
                          )}
                        </div>
                      </ScrollArea>
                    ) : (
                      <ProjectModification language={language as 'en' | 'ja'} />
                    )}
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    <Button variant="outline" onClick={() => window.location.reload()}>
                      {t.startNewAnalysis}
                    </Button>
                  </CardFooter>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
}
