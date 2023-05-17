import { InjectionToken } from '@angular/core';
import { environment } from 'src/environments/environment';

export const API_HOST = new InjectionToken<string>('apiHost', {
    providedIn: 'root',
    factory: () => environment.apiHost,
  });