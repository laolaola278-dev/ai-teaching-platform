import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

type Props = {
  content: string
}

export const MarkdownViewer: React.FC<Props> = ({ content }) => {
  return (
    <div style={{ padding: 8 }}>
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]} children={content} />
    </div>
  )
}
