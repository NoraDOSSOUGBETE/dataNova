/**
 * Service API pour l'authentification
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  role: 'juridique' | 'decisive';
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'juridique' | 'decisive';
}

export interface LoginResponse {
  user: User;
  token: string;
}

class AuthService {
  /**
   * Connexion utilisateur avec API réelle
   */
  async login(credentials: LoginCredentials): Promise<User> {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Identifiants invalides');
    }

    const data: LoginResponse = await response.json();
    
    // Stocker le token et l'utilisateur
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data.user;
  }

  /**
   * Inscription utilisateur
   */
  async register(data: RegisterData): Promise<User> {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      // Gérer les erreurs de validation Pydantic (detail peut être un tableau)
      let errorMessage = 'Erreur lors de l\'inscription';
      if (error.detail) {
        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else if (Array.isArray(error.detail)) {
          // Erreurs de validation Pydantic
          errorMessage = error.detail.map((e: any) => e.msg || e.message).join(', ');
        }
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  }

  /**
   * Déconnexion
   */
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  }

  /**
   * Récupère le token
   */
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Récupère l'utilisateur connecté
   */
  getUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Vérifie si l'utilisateur est authentifié
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();
