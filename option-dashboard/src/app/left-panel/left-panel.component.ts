// src/app/left-panel/left-panel.component.ts
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { ChartDataService } from '../chart-data.service';
import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { API_HOST } from '../injection-tokens';

@Component({
  selector: 'app-left-panel',
  templateUrl: './left-panel.component.html',
  styleUrls: ['./left-panel.component.css'],
})
export class LeftPanelComponent implements OnInit {
  @Input() strike: number = 300;
  @Input() triggerTmax: number = 40;
  @Input() startYear: number = 2000;

  futureValue: number = 0;
  apiUrl: string;

  @Output() dataSubmitted = new EventEmitter<any>();

  constructor(private chartDataService: ChartDataService, private http: HttpClient, @Inject(API_HOST) apiHost: string) { 
    this.apiUrl = `${apiHost}/future`
  }

  onSubmit(): void {
    const data = {
      strike: this.strike,
      triggerTmax: this.triggerTmax,
      startYear: this.startYear
    }
    this.chartDataService.emitDataSubmitted(data);

  }

  getFuture(): void {
    
    this.http.get(this.apiUrl).subscribe((response: any) => {
        if (response.success) {
            this.futureValue = response.future;
        } else {
            this.futureValue = 0
        }
    });
}


  ngOnInit(): void {

  }
}
