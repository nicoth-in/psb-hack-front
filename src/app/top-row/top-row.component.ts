import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-top-row',
  templateUrl: './top-row.component.html',
  styleUrls: ['./top-row.component.css']
})
export class TopRowComponent implements OnInit {

  title = "Верификация документов";
  subtitle = "Управление верефикацией ассетов";

  constructor() { }

  ngOnInit(): void {
  }

}
