import { Component, OnInit } from '@angular/core';
import { ApiService } from "../api.service";

@Component({
  selector: 'app-file-explorer',
  templateUrl: './file-explorer.component.html',
  styleUrls: ['./file-explorer.component.css']
})
export class FileExplorerComponent implements OnInit {

  fsobjects: any = [];
  path: any = [];

  constructor(
    private api: ApiService
  ) {}

  ngOnInit(): void {
    this.updatePath()
  }

  goToPathByIndex(i: number) {
    this.path = this.path.slice(0, i);
    this.updatePath();
  }

  folderUp(name: string) {
    this.path.push(name);
    this.updatePath()
  }

  verificateThis(name: string) {
    let path: any = [ ...this.path ];
    path.push(name);
    this.api.verificatePath(path).then(
      r => {
        console.log(r);
      }
    )
  }

  updatePath() {
     this.api.getPathContent(this.path).then(r => { this.fsobjects = r })
  }

}
