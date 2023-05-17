import { Inject, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LeftPanelComponent } from './left-panel/left-panel.component';
import { HttpClientModule } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { ChartModule } from 'angular-highcharts';
import { ChartPanelComponent } from './chart-panel/chart-panel.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

@NgModule({
  declarations: [
    AppComponent,
    LeftPanelComponent,
    ChartPanelComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    ChartModule,
    BrowserAnimationsModule
  ],
  providers: [
    { provide: 'API_HOST', useValue: environment.apiHost}
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
