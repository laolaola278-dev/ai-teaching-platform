import React from 'react';
import ReactMarkdown from 'react-markdown';
import 'katex/dist/katex.min.css';
import { KaTeX } from 'katex';

type Props = {
  content: string;
};

// Simple Markdown viewer; KaTeX can be extended via rehype-katex for full math rendering.
export const MarkdownViewer: React.FC<Props> = ({ content }) => {
  return (
    <div style={{ padding: 8 }}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};
