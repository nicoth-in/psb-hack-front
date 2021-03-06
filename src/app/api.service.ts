import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  
  //private baseJavaApi = "http://192.168.165.76:8080";
  // private baseVerifyApi = "http://172.20.10.5:8085";
  // private baseWs = "ws://172.20.10.5:8085/verify";

  private baseVerifyApi = "http://127.0.0.1:8085";
  private baseWs = "ws://127.0.0.1:8085/verify";

  constructor() {
    
  }

  async getPathContent(path: [string] | []) {

    let name: string = "" + path.join("/");
    let resp = await fetch(this.baseVerifyApi + "/files/?name=" + name);
    let jresp = await resp.json();

    let output: any = [];

    const updateOutput = (from: any, type: string) => {
      for (let fs_obj_name of from) {
        output.push(
          {
            name: fs_obj_name,
            type
          }
        )
      }
    }

    updateOutput(jresp.folders, "folder");
    updateOutput(jresp.files, "file");

    return output;

    // MVP prop
    //let name: string = '';

    // const example_tree: any = [
    //   {
    //     name: "My folder",
    //     type: 'folder',
    //     content: [
    //       {
    //         name: "Folder1",
    //         type: 'folder',
    //         content: [
    //           {
    //             name: "File1.png",
    //             type: 'file',
    //           }
    //         ]
    //       },
    //       {
    //         name: "Folder2",
    //         type: 'folder',
    //         content: [
    //           {
    //             name: "File2.png",
    //             type: 'file',
    //           }
    //         ]
    //       }
    //     ]
    //   }
    // ];

    // const getPath = (tree: any, pname: string) => {

    //   for (let obj of tree) {
    //     if ( obj.name === pname ) {
    //       return obj.content;
    //     }
    //   }

    // };

    // const getContents = (content: any) => {

    //   let response = [];

    //   for (let obj of content) {

    //     response.push({
    //       name: obj.name,
    //       type: obj.type
    //     });

    //   }

    //   return response;
    // };

    // var go_throw: any = example_tree;

    // for (let p of path) {
    //   go_throw = getPath(go_throw, p);
    // }

    // return getContents(go_throw);

  }

  verificatePath(path: [string]) {

    let file_path: string = "" + path.join("/");
    // let resp = await fetch(this.baseVerifyApi + "/verify/?path=" + file_path);
    // let jresp = await resp.json();

    var ws = new WebSocket(this.baseWs);
    
    ws.onopen = () => {
      ws.send(file_path);
    }

    return ws;
  }

}
