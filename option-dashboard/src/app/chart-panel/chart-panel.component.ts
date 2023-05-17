import { Component, OnInit, ViewChild } from '@angular/core';
import { ChartDataService } from '../chart-data.service';
import { LeftPanelComponent } from '../left-panel/left-panel.component';
import * as Highcharts from 'highcharts'
import HC_exporting from 'highcharts/modules/exporting';
import HC_exportData from 'highcharts/modules/export-data';

HC_exporting(Highcharts);
HC_exportData(Highcharts);
declare var google: any;

@Component({
  selector: 'app-chart-panel',
  templateUrl: './chart-panel.component.html',
  styleUrls: ['./chart-panel.component.css']
})
export class ChartPanelComponent implements OnInit {
  lat = -33.95;
  lng = 151.17;
  annualChartData: any;
  dailyChartData: any;
  annualChart: any;
  dailyChart: any;
  element: any;
  loading: boolean = false;
  seriesData = [];

  @ViewChild(LeftPanelComponent, { static: false }) leftPanel!: LeftPanelComponent;

  constructor(private chartDataService: ChartDataService) { }

  ngOnInit(): void {

    var map = new google.maps.Map(document.getElementById("map"), {
      zoom: 4,
      center: { lat: this.lat, lng: this.lng },
    });

    new google.maps.Marker({
      position: { lat: this.lat, lng: this.lng },
      map,
    });

    this.chartDataService.dataSubmitted$.subscribe(data => {
      this.loading = true;
      this.chartDataService.submitData(data).subscribe(
        data => {
          this.annualChartData = data.annualChartData;
          this.dailyChartData = data.dailyChartData;

          this.loading = false;

          console.log(this.annualChartData);
          console.log(this.dailyChartData);
          
          let seriesData = []
          for (let year in this.dailyChartData) {
            if (this.dailyChartData.hasOwnProperty(year)) {
              seriesData.push({
                name: year,
                data: this.dailyChartData[year],
                type: 'column',
              });
            }
          }

          this.createAnnualChart();
          this.createDailyChart(seriesData);

        },
        error => {
          console.error('Error:', error);
          this.loading = false;
        }
      );
    });
  }

  createAnnualChart(): void {
    if (this.annualChart != undefined) {
      this.element = document.getElementsByClassName("highcharts-data-table")
      console.log(this.element)
      this.element[0].remove()
    }
    this.annualChart = Highcharts.chart('annual-chart-container', {
      title: {
        text: 'Annual Payout',
      },
      exporting: {
        showTable: true
      },
      xAxis: {
        title: {
          text: 'Years',
        },
        accessibility: {
          rangeDescription: 'range',
        },
        categories: this.annualChartData.YEAR,
      },
      yAxis: {
        title: {
          text: 'Payout (USD)',
        },
        labels: {
          format: '${value}',
        }
      },
      series: [
        {
          name: 'Payout',
          data: this.annualChartData.PAYOUT,
          type: 'column',
        },
      ],
    });
  }

  createDailyChart(seriesData: any): void {
    this.dailyChart = Highcharts.chart('daily-chart-container', {
      title: {
        text: 'Daily Payout by Year',
        align: 'center'
      },
      xAxis: [{
        title: {
          text: 'Dates',
        }
      }],
      yAxis: [{ // Primary yAxis
        labels: {
          format: '${value}',
        },
        title: {
          text: 'Payout',
        },
      }, { // Secondary yAxis
        title: {
          text: 'Daily T-max',
        },
        labels: {
          format: '{value}°C',
        },
        opposite: true
      }],
      tooltip: {
        shared: true
      },
      legend: {
        align: 'left',
        x: 80,
        verticalAlign: 'top',
        y: 80,
        floating: false,
      },
      series: seriesData,
    });
  }


}
