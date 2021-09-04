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
  maxLoading: number = 0;
  currentLoading: number = 0;

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

    const callback = (ev: any) => {
      let resp = JSON.parse(ev.data);
      if (resp.type === "current") {
        this.currentLoading = resp.msg;
        if (this.currentLoading == this.maxLoading) {
          
        }
      } else {
        this.maxLoading = resp.msg;
      }
    };

    let ws = this.api.verificatePath(path);

    ws.onmessage = callback;

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
