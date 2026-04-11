import React, { useEffect, useRef } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { EditorState } from '@codemirror/state';
import { EditorView as CMView } from '@codemirror/view';
import { CodeMirror } from '@uiw/react-codemirror';

type Props = {
  value?: string;
  onChange?: (v: string) => void;
};

export const CodeEditor: React.FC<Props> = ({ value = '', onChange }) => {
  return (
    <CodeMirror
      height="400px"
      value={value}
      extensions={[javascript() as any]}
      onChange={(val) => onChange?.(val)}
    />
  );
};
