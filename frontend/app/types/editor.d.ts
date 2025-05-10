// frontend/types/editor.d.ts
declare module 'monaco-editor' {
    export namespace editor {
      interface IStandaloneCodeEditor {
        getModel(): any;
        executeEdits(source: string, edits: any[]): void;
        // Add other methods you use
      }
    }
  }