/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_VERSION: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_DEBUG: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_ERROR_TRACKING: string;
  readonly VITE_THEME: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_DEFAULT_PAGE_SIZE: string;
  readonly VITE_MAX_PAGE_SIZE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}