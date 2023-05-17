import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { API_HOST } from './injection-tokens';

@Injectable({
  providedIn: 'root',
})
export class ChartDataService {
  private apiUrl: string;
  private dataSubmittedSource = new Subject<any>();
  dataSubmitted$ = this.dataSubmittedSource.asObservable();

  constructor(private http: HttpClient, @Inject(API_HOST) apiHost: string) {
    this.apiUrl = `${apiHost}/process`;
  }

  submitData(data: any): Observable<any> {
    const headers = new HttpHeaders()
      .set('Content-Type', 'application/json');

    return this.http.post(`${this.apiUrl}`, data, { headers: headers });
    
  }

  emitDataSubmitted(data: any): void {
    this.dataSubmittedSource.next(data);
  }
}
