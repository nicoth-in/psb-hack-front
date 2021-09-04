import { Component, OnChanges } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'psb-hack-front';

  onFilesLoaded(event: any) {

    const files: [File] = event.target.files;

    console.log(files);


  }
}
