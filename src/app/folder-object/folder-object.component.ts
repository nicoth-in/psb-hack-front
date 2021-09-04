import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-folder-object',
  templateUrl: './folder-object.component.html',
  styleUrls: ['./folder-object.component.css']
})

export class FolderObjectComponent implements OnInit {

  
  @Input() name = '';

  constructor() { }

  ngOnInit(): void {
  }

}
