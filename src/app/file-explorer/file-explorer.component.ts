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
  hasSelected: boolean = false;

  constructor(
    private api: ApiService
  ) {}

  ngOnInit(): void {
    this.updatePath()
  }

  selectObj(name: string) {
    let hasSelected = false;

    for (let fs_obj of this.fsobjects) {

      if (fs_obj.name == name) {
        fs_obj.selected = !fs_obj.selected;
      };

      hasSelected = hasSelected || fs_obj.selected;
    }

    this.hasSelected = hasSelected;
  }

  goToPathByIndex(i: number) {
    this.path = this.path.slice(0, i);
    this.updatePath();
  }

  folderUp(name: string) {
    this.path.push(name);
    this.updatePath()
  }

  verificateSelected() {
    for (let fs_o of this.fsobjects) {
      if (fs_o.selected) {
        this.verificateOne(fs_o.name);
      }
    }
  }

  verificateOne(name: string) {
    let path: any = [ ...this.path ];
    path.push(name);
    this.api.verificatePath(path).then(
      r => {
        console.log(r);
      }
    )
  }

  updatePath() {
     this.api.getPathContent(this.path).then(r => { 

      for (let o of r) {
        o.selected = false;
      }
       
      this.fsobjects = r;
      this.hasSelected = false;
      
     })
  }

}
