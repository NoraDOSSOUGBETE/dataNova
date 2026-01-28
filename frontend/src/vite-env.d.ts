/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_DEBUG: string;
  readonly VITE_MODE: 'mock' | 'api';
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
