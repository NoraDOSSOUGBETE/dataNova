/**
 * Configuration de l'application
 */

export const config = {
  // URL de l'API backend
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
};

// Log de la configuration au démarrage
console.log('🔧 Configuration:', {
  apiUrl: config.apiUrl,
});
