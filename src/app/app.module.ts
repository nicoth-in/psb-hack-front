import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TopRowComponent } from './top-row/top-row.component';
import { FileExplorerComponent } from './file-explorer/file-explorer.component';
import { FileObjectComponent } from './file-object/file-object.component';
import { FolderObjectComponent } from './folder-object/folder-object.component';

@NgModule({
  declarations: [
    AppComponent,
    TopRowComponent,
    FileExplorerComponent,
    FileObjectComponent,
    FolderObjectComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
